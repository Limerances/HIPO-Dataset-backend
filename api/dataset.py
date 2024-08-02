from flask import Flask,Blueprint ,request,send_file, Response
from database.database import *
from tool.my_token import *
from tool.tool import *
from threading import Thread
import subprocess
import shlex
import datetime

bp = Blueprint('dataset', __name__, url_prefix='/dataset')

#获取数据集列表
@bp.route('/getList', methods=["POST"])
def getList():
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
                    datasets = Dataset.query.filter_by(is_active=True).all()
                    if datasets == None:
                        result = { "errno": ErrnoType.info, "message": "不存在数据集" }
                    else:
                        in_data = []
                        for dataset in datasets:
                            param_info_list = []
                            # for param_info in dataset.param_infos:
                            #将选项按param_index排序，并且只返回用户可选的参数
                            for param_info in ParamInfo.query.filter_by(is_active=True,dataset_id=dataset.id,is_chosen_by_user=True)\
                                .order_by(ParamInfo.param_index).all():
                                #只返回用户可选的参数
                                param_value_option_list = []
                                # for param_value_option in param_info.param_value_options:
                                # 将is_default == True的选项放在最前面,其他按原序
                                for param_value_option in sorted(param_info.param_value_options, key=lambda x: 0 if x.is_default else 1):
                                    param_value_option_list.append({
                                        "name": param_value_option.name,
                                        "value": param_value_option.value,
                                        "is_default": param_value_option.is_default,
                                    })
                                param_info_list.append({
                                    "name": param_info.name,
                                    "param_index": param_info.param_index,
                                    "param_value_option": param_value_option_list,
                                })
                            in_data.append({
                                "id": dataset.id,
                                "title": dataset.title,
                                "abstract": dataset.abstract,
                                "param_info": param_info_list,
                            })
                        result = { "errno": ErrnoType.success, "message": "获取成功" }
                        result["data"] = in_data
        return convert(result)
    else:
        result = {"errno": ErrnoType.faliure, "message": "前端炸了"}
        return convert(result)
    
#申请下载数据集局部
@bp.route('/apply', methods=["POST"])
def apply():
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
                    dataset_id = data['dataset_id']
                    dataset = Dataset.query.filter_by(is_active=True,id=dataset_id).first()
                    if dataset == None:
                        result = { "errno": ErrnoType.info, "message": "数据集不存在" }
                    else:
                        #[{"name":"param1","value":"value1",param_index}]
                        param_value_list = []
                        for param_value in data['param_value_list']:
                            param_value_list.append({
                                "name": param_value['name'],
                                "value": param_value['value'],
                                "param_index": param_value['param_index'],
                            })
                        #补全不由user决定的参数，is_chosen_by_user == False
                        for param_info in dataset.param_infos:
                            if param_info.is_chosen_by_user == False:
                                param_value_list.append({
                                    "name": param_info.name,
                                    "value": param_info.param_value_options[0].value,
                                    "param_index": param_info.param_index,
                                })
                        if len(dataset.param_infos) != len(param_value_list):
                            result = { "errno": ErrnoType.faliure, "message": "参数数量不匹配" }
                        else:
                            empty = False
                            for param_value in param_value_list:
                                if param_value['name'] == "" or param_value['value'] == "" or param_value['param_index'] == "":
                                    empty = True
                                    break
                            if empty:
                                result = { "errno": ErrnoType.faliure, "message": "参数不能为空" }
                            else:
                                
                                dataset_download_part = DatasetDownloadPart(
                                    apply_time = datetime.datetime.now(),
                                    account_id = id,
                                    dataset_id = dataset_id,
                                )
                                db.session.add(dataset_download_part)
                                db.session.flush()
                                add_list = []
                                param_value_list = sorted(param_value_list, key=lambda x: x['param_index'])
                                temp_param_infos = sorted(dataset.param_infos, key=lambda x: x.param_index)
                                for i in range(len(param_value_list)):
                                    add_list.append(ParamValue(
                                        value=param_value_list[i]['value'],
                                        param_info_id=temp_param_infos[i].id,
                                        dataset_download_part_id=dataset_download_part.id,
                                    ))
                                db.session.add_all(add_list)
                                db.session.commit()
                                
                                thread = Thread(target=generate_file, args=(dataset,dataset_download_part,param_value_list,))
                                thread.start()
                                
                                result = { "errno": ErrnoType.success, "message": "申请成功" }
        return convert(result)
    else:
        result = {"errno": ErrnoType.faliure, "message": "前端炸了"}
        return convert(result)
        
def generate_file(dataset,dataset_download_part,param_value_list):
    app = Flask(__name__)
    app.config.from_object(settings.Configs)
    db.init_app(app)
    with app.app_context():
        cmd_exe = "/ssd/dsk/JSI-Toolkit/build/tool/jsiconvert/jsiextract"
        cmd_param = " ".join([" --" + param_value["name"] + " " + param_value["value"] for param_value in param_value_list])
        # real_cmd = cmd_exe + cmd_param
        real_cmd = 'echo "{cmd_param}" > temp/acmd.txt'.format(cmd_param=cmd_param)
        run_bash = "bash script/create_download_part.sh '{real_cmd}'".format(real_cmd=real_cmd)
        try:
            print(run_bash)
            result = subprocess.run(shlex.split(run_bash),check=True, capture_output=True, text=True)
            print(result)
            dataset_download_part.type = DatasetDownloadPartType.generated
            dataset_download_part.generate_time = datetime.datetime.now()
            dataset_download_part.download_url = "/root/Web/hipo_backend/temp/acmd.txt"#待定###########################################################
            db.session.add(dataset_download_part)
            db.session.commit()
            
        except subprocess.CalledProcessError as e:
            
            dataset_download_part.type = DatasetDownloadPartType.error
            dataset_download_part.bash_stdout = e.stdout
            dataset_download_part.bash_stderr = e.stderr
            db.session.add(dataset_download_part)
            db.session.commit()
        
#获取数据集下载列表
@bp.route('/getAppliedList', methods=["POST"])
def getAppliedList():
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
                    #order by update_time desc
                    dataset_download_parts = DatasetDownloadPart.query.filter_by(
                        is_active=True, account_id=id
                        ).order_by(DatasetDownloadPart.update_time.desc()).all()
                    # dataset_download_parts = DatasetDownloadPart.query.filter_by(is_active=True,account_id=id).all()
                    if dataset_download_parts == None:
                        result = { "errno": ErrnoType.info, "message": "不存在数据下载项下载记录" }
                    else:
                        in_data = []
                        for dataset_download_part in dataset_download_parts:
                            param_value_list = []
                            #只返回用户可编辑的参数
                            for param_value in dataset_download_part.param_values:
                                if param_value.param_info.is_chosen_by_user:
                                    param_value_list.append({
                                        "name": param_value.param_info.name,
                                        "value": param_value.value,
                                    })
                            in_data.append({
                                "id": dataset_download_part.id,
                                "title": dataset_download_part.dataset.title,
                                "abstract": dataset_download_part.dataset.abstract,
                                "type": dataset_download_part.type,
                                "apply_time": dataset_download_part.apply_time,
                                "generate_time": dataset_download_part.generate_time,
                                "param_value_list": param_value_list,
                            })
                        result = { "errno": ErrnoType.success, "message": "获取成功" }
                        result["data"] = in_data
        return convert(result)
    else:
        result = {"errno": ErrnoType.faliure, "message": "前端炸了"}
        return convert(result)

@bp.route('/getSecureKey', methods=["POST"])
def getSecureKey():
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
                    dataset_download_part_id = data['id']
                    dataset_download_part = DatasetDownloadPart.query.filter_by(
                        is_active=True, account_id=id, id=dataset_download_part_id
                        ).first()
                    if dataset_download_part == None:
                        result = { "errno": ErrnoType.info, "message": "数据下载项不存在" }
                    else:
                        result = { "errno": ErrnoType.success, "message": "获取成功" }
                        result["data"] = {
                            "secure_key": dataset_download_part.secure_key,
                        }
        return convert(result)
    else:
        result = {"errno": ErrnoType.faliure, "message": "前端炸了"}
        return convert(result)

@bp.route('/downloadDataset', methods=["POST","GET"])
def downloadDataset():
    header = request.headers
    token = request.args.get("token")
    id = request.args.get("id")
    secure_key = request.args.get("secure_key")
    dataset_download_part_id = request.args.get("dataset_download_part_id")
    
    if token == None:
        result = {"errno": ErrnoType.login_failure, "message": "未登录"}
    else:
        id, valid_id = convert_int(id)
        dataset_download_part_id, valid_dataset_download_part_id = convert_int(dataset_download_part_id)
        if not valid_id or not valid_dataset_download_part_id:
            result = { "errno": ErrnoType.login_failure, "message": "登录失效(ID)" }
        else:
            valid = check_token(id,token)
            if not valid:
                result = {"errno": ErrnoType.login_failure, "message": "登录失效"}
            else:
                dataset_download_part = DatasetDownloadPart.query.filter_by(
                    is_active=True, account_id=id, id=dataset_download_part_id
                    ).first()
                if dataset_download_part == None:
                    result = { "errno": ErrnoType.faliure, "message": "数据下载项不存在" }
                else:
                    if dataset_download_part.type != DatasetDownloadPartType.generated:
                        result = { "errno": ErrnoType.faliure, "message": "下载失败" }
                    else:
                        if dataset_download_part.secure_key != secure_key:
                            result = { "errno": ErrnoType.faliure, "message": "数据下载项验证失败" }
                        else:
                            result = { "errno": ErrnoType.success, "message": "下载成功" }
                            
                            dataset_download_part.secure_key = generate_secure_random_string()
                            db.session.commit()

                            def getFileName():
                                name = dataset_download_part.dataset.title
                                for param_value in dataset_download_part.param_values:
                                    if param_value.param_info.is_chosen_by_user:
                                        name += " --" + param_value.param_info.name + " " + param_value.value
                                from urllib.parse import quote
                                return quote(name)
                            filename = getFileName()
                            
                            #方法一，一看就不行……
                            # return send_file(dataset_download_part.download_url, as_attachment=True)
                            #方法二
                            def send_file():
                                store_path = dataset_download_part.download_url
                                with open(store_path, 'rb') as targetfile:
                                    while 1:
                                        data = targetfile.read(20 * 1024 * 1024)  # 每次读取20M
                                        if not data:
                                            break
                                        yield data
                            response = Response(send_file(), content_type='application/octet-stream')
                            response.headers["Content-disposition"] = 'attachment; filename=%s' % filename
                            return response
        return convert(result)
