import os
import json

from flask import Flask,send_file
from flask import url_for
from flask import session
from markupsafe import escape

# from hipo_backend import settings
# from hipo_backend import database
import settings
from database.database import *
from tool.tool import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
# def create_app():
# create and configure the app
app = Flask(__name__)

app.config.from_object(settings.Configs)

db.init_app(app)

# a simple page that says hello
@app.route('/hello')
def hello():
    return 'Hello, World!'

# @app.route('/download')
# def download_file():
#     file_path = r'/root/Web/flaskr/14239217943907926016_20240529003042_1.png'   # 服务器端的文件路径和文件名
#     return send_file(file_path, as_attachment=True)

# from . import db
# db.init_app(app)

import api.test_api 
app.register_blueprint(api.test_api.bp)

import api.auth
app.register_blueprint(api.auth.bp)

import api.user
app.register_blueprint(api.user.bp)

import api.admin
app.register_blueprint(api.admin.bp)

import api.dataset
app.register_blueprint(api.dataset.bp)

# return app ,db

# def my_commit(item):
#     with app.app_context():
#         db.session.add(item)
#         db.session.flush()
#         db.session.commit()
#     return item

def create_tables():
    with app.app_context():
        db.create_all()

# def init_data():
#     item_list = load_data()
#     # acc = Account(email="superadmin@buaa.edu.cn",password="arimakana",username="superadmin",agencyName="管理员",type=UserType.super_admin,register_id=1)
#     with app.app_context():
#         db.session.add_all(item_list)
#         db.session.commit()

def init_tables():
    with app.app_context():
        db.drop_all()
        db.create_all()
        init_data()

def init_data():
    with app.app_context():
    # item_list = []
        with open('init.json','r') as file:
            data = json.load(file)
            for account in data["accounts"]:
                acc = Account(
                    email=account["email"],
                    password=md5_salt(account["password"]),
                    username=account["username"],
                    agencyName=account["agencyName"],
                    type=UserType(account["type"]),
                    register_id=account["register_id"]
                )
                db.session.add(acc)
                db.session.flush()
            for dataset in data["datasets"]:
                ds = Dataset(
                    title=dataset["title"],
                    abstract=dataset["abstract"],
                    url=dataset["url"]
                )
                db.session.add(ds)
                db.session.flush()
                for param_info in dataset["param_infos"]:
                    pi = ParamInfo(
                        name=param_info["name"],
                        param_index=param_info["param_index"],
                        dataset_id=ds.id,
                        is_chosen_by_user=param_info["is_chosen_by_user"]
                    )
                    db.session.add(pi)
                    db.session.flush()
                    for param_value_option in param_info["param_value_options"]:
                        pvo = ParamValueOption(
                            name=param_value_option["name"],
                            value=param_value_option["value"],
                            is_default=param_value_option["is_default"],
                            param_info_id=pi.id
                        )
                        db.session.add(pvo)
                        db.session.flush()
        db.session.commit()
        

if __name__ == '__main__':
    # --port 52000 --host=0.0.0.0 --debug
    app.run(port=52001, host='0.0.0.0') 
    # app.run(port=52001, host='0.0.0.0', debug=True) 
    