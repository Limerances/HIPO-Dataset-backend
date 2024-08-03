from flask import Blueprint ,request
from database.database import *
from tool.my_token import *
from tool.tool import *

bp = Blueprint('test', __name__, url_prefix='/test')

@bp.route('/basetest', methods=["GET","POST"])
def test():
    try:
        # data = request.json
        # header = request.headers
        # print(data)
        # print(header)
        # print(header.get("Token"))
        # print(header.get("Uid"))
        result = { "errno": ErrnoType.success, "message": "成功" }
        return convert(result)
    except:
        result = { "errno": ErrnoType.faliure, "message": "失败" }
        return convert(result)
    
@bp.route('/adminactive', methods=["GET","POST"])
def adminactive():
    acc = Account.query.filter_by(id=1).first()
    if acc.is_active == True:
        acc.is_active = False
    else:
        acc.is_active = True
    db.session.commit()
    result = { "errno": ErrnoType.success, "message": "成功" }
    return convert(result)