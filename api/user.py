from flask import Blueprint ,request
from database.database import *
from tool.my_token import *
from tool.tool import *

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/userInfo', methods=["POST"])
def userInfo():
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
                    account = Account.query.filter_by(is_active=True,id=id).first()
                    if account == None:
                        result = { "errno": ErrnoType.faliure, "message": "账号不存在" }
                    else:
                        in_data = {
                            "id": account.id,
                            "username": account.username,
                            "email": account.email,
                            "avatar": account.avatar,
                            "agencyName": account.agencyName,
                            "type": account.type
                        }
                        result = { "errno": ErrnoType.success, "message": "获取成功" }
                        result["data"] = in_data
        return convert(result)
    else:
        result = {"errno": ErrnoType.faliure, "message": "前端炸了"}
        return convert(result)
    
@bp.route('/changePassword', methods=["POST"])
def changePassword():
    if request.method == 'POST':
        data = request.json
        header = request.headers
        token = header.get("Token")

        oldPassword = data["oldPassword"]
        newPassword = data["newPassword"]
        if token == None:
            result = { "errno": ErrnoType.login_faliure, "message": "未登录" }
        else:
            id, valid = convert_int(header.get("Uid"))
            if not valid:
                result = { "errno": ErrnoType.login_failure, "message": "登录失效(ID)" }
            else:
                valid = check_token(id,token)
                if not valid:
                    result = { "errno": ErrnoType.login_faliure, "message": "登录失效" }
                else:
                    account = Account.query.filter_by(is_active=True,id=id).first()
                    if account == None:
                        result = { "errno": ErrnoType.faliure, "message": "账号不存在" }
                    else:
                        if account.password != oldPassword:
                            result = { "errno": ErrnoType.faliure, "message": "密码错误" }
                        else:
                            account.password = newPassword
                            db.session.commit()
                            result = { "errno": ErrnoType.success, "message": "修改成功" }
        return convert(result)
    else:
        result = {"errno": ErrnoType.faliure, "message": "前端炸了"}
        return convert(result)