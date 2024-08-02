from flask import Blueprint ,request
from database.database import *
from tool.my_token import *
from tool.tool import *

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/getUserList', methods=["POST"])
def getUserList():
    if request.method == 'POST':
        data = request.json
        header = request.headers
        token = header.get("Token")

        need_type = data['type']
        if token == None:
            result = {"errno": ErrnoType.login_failure, "message": "未登录"}
        else:
            id, valid = convert_int(header.get("Uid"))
            if not valid:
                result = { "errno": ErrnoType.login_failure, "message": "登录失效(ID)" }
            else:
                valid = check_token(id,token)
                if not valid:
                    result = {"errno": ErrnoType.login_failure, "message": "登录失效"}
                else:
                    token_data = get_info(token)
                    id = token_data['id']
                    type = UserType(token_data['type'])
                    need_type = UserType(int(need_type))
                    if need_type.value >= type.value:
                        result = {"errno": ErrnoType.faliure, "message": "权限不足"}
                    else:
                        account = Account.query.filter_by(is_active=True,type=need_type).all()
                        in_data = []
                        for i in account:
                            in_data.append({
                                "id": i.id,
                                "username": i.username,
                                "email": i.email,
                                "avatar": i.avatar,
                                "agencyName": i.agencyName,
                                "type": i.type,
                                "is_active": i.is_active,
                                "create_time": i.create_time,
                            })
                        result = {"errno": ErrnoType.success, "message": "获取成功"}
                        result["data"] = in_data
        return convert(result)
    else:
        result = {"errno": ErrnoType.faliure, "message": "前端炸了"}
        return convert(result)
    
@bp.route('/getLogs', methods=["POST"])
def getLogs():
    if request.method == 'POST':
        data = request.json
        header = request.headers
        token = header.get("Token")

        if token == None:
            result = {"errno": ErrnoType.login_failure, "message": "未登录"}
        else:
            id, valid = convert_int(header.get("Uid"))
            if not valid:
                result = { "errno": ErrnoType.login_failure, "message": "登录失效(ID)" }
            else:
                valid = check_token(id,token)
                if not valid:
                    result = {"errno": ErrnoType.login_failure, "message": "登录失效"}
                else:
                    token_data = get_info(token)
                    id = token_data['id']
                    type = UserType(token_data['type'])
                    if type != UserType.super_admin or type != UserType.admin:
                        result = {"errno": ErrnoType.faliure, "message": "权限不足"}
                    else:
                        #order by update_time desc
                        dataset_download_parts = DatasetDownloadPart.query.filter_by(
                            is_active=True
                            ).order_by(DatasetDownloadPart.update_time.desc()).all()
                        # dataset_download_parts = DatasetDownloadPart.query.filter_by(is_active=True,account_id=id).all()
                        if dataset_download_parts == None:
                            result = { "errno": ErrnoType.info, "message": "不存在数据下载项下载记录" }
                        else:
                            in_data = []
                            for dataset_download_part in dataset_download_parts:
                                param_value_list = []
                                for param_value in dataset_download_part.param_values:
                                    param_value_list.append({
                                        "name": param_value.param_info.name,
                                        "value": param_value.value,
                                    })
                                account_info = {
                                    "id": dataset_download_part.account.id,
                                    "username": dataset_download_part.account.username,
                                    "email": dataset_download_part.account.email,
                                    "avatar": dataset_download_part.account.avatar,
                                    "agencyName": dataset_download_part.account.agencyName,
                                    "type": dataset_download_part.account.type,
                                    "is_active": dataset_download_part.account.is_active,
                                }
                                in_data.append({
                                    "id": dataset_download_part.id,
                                    "name": dataset_download_part.dataset.title,
                                    "abstract": dataset_download_part.dataset.abstract,
                                    "type": dataset_download_part.type,
                                    "apply_time": dataset_download_part.apply_time,
                                    "generate_time": dataset_download_part.generate_time,
                                    "param_value_list": param_value_list,
                                    "user_info": account_info,
                                })
                            result = { "errno": ErrnoType.success, "message": "获取成功" }
                            result["data"] = in_data
        return convert(result)
    else:
        result = {"errno": ErrnoType.faliure, "message": "前端炸了"}
        return convert(result)
    
@bp.route('/disableUser', methods=["POST"])
def disableUser():
    if request.method == 'POST':
        data = request.json
        header = request.headers
        token = header.get("Token")

        disable_id = data['id']
        if token == None:
            result = {"errno": ErrnoType.login_failure, "message": "未登录"}
        else:
            id, valid = convert_int(header.get("Uid"))
            if not valid:
                result = { "errno": ErrnoType.login_failure, "message": "登录失效(ID)" }
            else:
                valid = check_token(id,token)
                if not valid:
                    result = {"errno": ErrnoType.login_failure, "message": "登录失效"}
                else:
                    token_data = get_info(token)
                    id = token_data['id']
                    type = UserType(token_data['type'])
                    account = Account.query.filter_by(is_active=True,id=disable_id).first()
                    if account == None:
                        result = {"errno": ErrnoType.faliure, "message": "用户不存在"}
                    else:
                        if type != UserType.super_admin or type != UserType.admin:
                            result = {"errno": ErrnoType.faliure, "message": "权限不足"}
                        else:
                            account.is_active = False
                            db.session.commit()
                            result = {"errno": ErrnoType.success, "message": "禁用成功"}
        return convert(result)
    else:
        result = {"errno": ErrnoType.faliure, "message": "前端炸了"}
        return convert(result)
    
@bp.route('/enableUser', methods=["POST"])
def enableUser():
    if request.method == 'POST':
        data = request.json
        header = request.headers
        token = header.get("Token")

        enable_id = data['id']
        if token == None:
            result = {"errno": ErrnoType.login_failure, "message": "未登录"}
        else:
            id, valid = convert_int(header.get("Uid"))
            if not valid:
                result = { "errno": ErrnoType.login_failure, "message": "登录失效(ID)" }
            else:
                valid = check_token(id,token)
                if not valid:
                    result = {"errno": ErrnoType.login_failure, "message": "登录失效"}
                else:
                    token_data = get_info(token)
                    id = token_data['id']
                    type = UserType(token_data['type'])
                    account = Account.query.filter_by(id=enable_id).first()
                    if account == None:
                        result = {"errno": ErrnoType.faliure, "message": "用户不存在"}
                    else:
                        if type != UserType.super_admin or type != UserType.admin:
                            result = {"errno": ErrnoType.faliure, "message": "权限不足"}
                        else:
                            if account.is_active == True:
                                result = {"errno": ErrnoType.info, "message": "用户已启用"}
                            else:
                                account.is_active = True
                                db.session.commit()
                                result = {"errno": ErrnoType.success, "message": "启用成功"}
        return convert(result)
    else:
        result = {"errno": ErrnoType.faliure, "message": "前端炸了"}
        return convert(result)