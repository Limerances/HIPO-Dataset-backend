from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from enum import Enum
from tool.tool import generate_secure_random_string

class ErrnoType(Enum):
    success = 0
    faliure = 1
    login_failure = 2
    info = 3
    

db = SQLAlchemy()

class UserType(Enum):
    user = 1
    admin = 2
    super_admin = 3

class Account(db.Model):
    __tablename__ = 'account'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    email = db.Column(db.String(256), nullable=False,unique=True)
    password = db.Column(db.String(256), nullable=False)
    username = db.Column(db.String(64), nullable=False)
    avatar = db.Column(db.String(256), nullable=False,\
        default='https://webplus-cn-shenzhen-s-61b04cecf968dd14ce73e9b4.oss-cn-shenzhen.aliyuncs.com/resource/avatar_scholar_128.png')
    agencyName = db.Column(db.String(256), nullable=False)
    type = db.Column(db.Enum(UserType), nullable = False,default=UserType.user)
    register_id = db.Column(db.Integer, nullable=True)
    dataset_download_parts = db.relationship('DatasetDownloadPart', backref='account',lazy=True) #relationship
    
    is_active = db.Column(db.Boolean, nullable=False,default=True)
    update_time = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    create_time = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'))
    
class Dataset(db.Model):
    __tablename__ = 'dataset'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    title = db.Column(db.String(256), nullable=False)
    abstract = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(256), nullable=False)
    param_infos = db.relationship('ParamInfo', backref='dataset', lazy=True) #relationship
    dataset_download_parts = db.relationship('DatasetDownloadPart', backref='dataset', lazy=True) #relationship
    
    is_active = db.Column(db.Boolean, nullable=False,default=True)
    update_time = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    create_time = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'))
    
class ParamInfo(db.Model):
    __tablename__ = 'param_info'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(256), nullable=False)
    param_index = db.Column(db.Integer, nullable=False)
    is_chosen_by_user = db.Column(db.Boolean, nullable=False,default=False)
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'), nullable=False) #foreign key
    param_value_options = db.relationship('ParamValueOption', backref='param_info', lazy=True) #relationship
    param_values = db.relationship('ParamValue', backref='param_info', lazy=True) #relationship
    
    is_active = db.Column(db.Boolean, nullable=False,default=True)
    update_time = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    create_time = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'))

class ParamValueOption(db.Model):
    __tablename__ = 'param_value_option'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(256), nullable=False)
    value = db.Column(db.String(256), nullable=False)
    is_default = db.Column(db.Boolean, nullable=False,default=False)
    param_info_id = db.Column(db.Integer, db.ForeignKey('param_info.id'), nullable=False) #foreign key
    
    is_active = db.Column(db.Boolean, nullable=False,default=True)
    update_time = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    create_time = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'))

class DatasetDownloadPartType(Enum):
    applied = 1
    generated = 2
    expired = 3
    error = 4

class DatasetDownloadPart(db.Model):
    __tablename__ = 'dataset_download_part'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    type = db.Column(db.Enum(DatasetDownloadPartType), nullable = False,default=DatasetDownloadPartType.applied)
    apply_time = db.Column(db.DateTime, nullable=False)
    generate_time = db.Column(db.DateTime)
    expire_time = db.Column(db.DateTime)
    download_url = db.Column(db.String(256))
    secure_key = db.Column(db.String(256),nullable=False,default=generate_secure_random_string)
    bash_stdout = db.Column(db.Text)
    bash_stderr = db.Column(db.Text)
    param_values = db.relationship('ParamValue', backref='dataset_download_part', lazy=True) #relationship
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False) #foreign key
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'), nullable=False) #foreign key
    
    is_active = db.Column(db.Boolean, nullable=False,default=True)
    update_time = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    create_time = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'))
    
class ParamValue(db.Model):
    __tablename__ = 'param_value'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    value = db.Column(db.String(256), nullable=False)
    param_info_id = db.Column(db.Integer, db.ForeignKey('param_info.id'), nullable=False) #foreign key
    dataset_download_part_id = db.Column(db.Integer, db.ForeignKey('dataset_download_part.id'), nullable=False) #foreign key
    
    is_active = db.Column(db.Boolean, nullable=False,default=True)
    update_time = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    create_time = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'))
    
