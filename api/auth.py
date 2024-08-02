from flask import Blueprint ,request
from database.database import *
from tool.my_token import *
from tool.tool import *

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=["POST"])
def login():
    if request.method == 'POST':
        data = request.json
        email = data['email']
        password = data['password']
        if email == None or password == None or email == "" or password == "":
            result = { "errno": ErrnoType.faliure, "message": "参数不能为空" }
        else:
            account = Account.query.filter_by(is_active=True,email=email).first()
            if account == None:
                result = { "errno": ErrnoType.faliure, "message": "账号不存在" }
            elif account.password != password:
                result = { "errno": ErrnoType.faliure, "message": "密码错误" }
            else:
                token = generate_token(account.id,account.email,account.username,account.type)
                result = { "errno": ErrnoType.success, "message": "登录成功", "token": token ,"id": account.id}
                in_data = {
                    "id": account.id,
                    "username": account.username,
                    "email": account.email,
                    "avatar": account.avatar,
                    "agencyName": account.agencyName,
                    "type": account.type
                }
                result["data"] = in_data
        return convert(result)
    else:
        result = {"errno": ErrnoType.faliure, "message": "前端炸了"}
        return convert(result)
            
@bp.route('/register', methods=["POST"])
def register():
    if request.method == 'POST':
        header = request.headers
        token = header.get("Token")
        
        data = request.json
        username = data['username']
        email = data['email']
        password = data['password']
        agencyName = data['agencyName']
        register_type = data['type']
        if token == None:
            result = { "errno": ErrnoType.login_failure, "message": "未登录" }
        else:
            id, valid = convert_int(header.get("Uid"))
            if not valid:
                result = { "errno": ErrnoType.login_failure, "message": "登录失效(ID)" }
            else:
                valid = check_token(id,token)
                if not valid:
                    result = { "errno": ErrnoType.login_failure, "message": "登录失效" }
                else:
                    token_data = get_info(token)
                    id = token_data['id']
                    type = UserType(token_data['type'])
                    register_type = UserType(int(register_type))
                    if register_type.value >= type.value:
                        result = { "errno": ErrnoType.faliure, "message": "权限不足" }
                    else:
                        account = Account.query.filter_by(email=email).first()
                        if account != None:
                            result = { "errno": ErrnoType.faliure, "message": "账号已存在" }
                        else:
                            acc = Account(email=email,password=password,username=username,agencyName=agencyName,type=register_type,register_id=id)
                            db.session.add(acc)
                            db.session.commit()
                            result = { "errno": ErrnoType.success, "message": "注册成功" }
        return convert(result)
    else:
        result = {"errno": ErrnoType.faliure, "message": "前端炸了"}
        return convert(result)