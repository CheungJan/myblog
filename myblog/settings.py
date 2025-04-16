"""
    :author: CheungJan (CJ)
    :url: http://cheungjan.com
    :copyright: ©2025 Cheung Jan <CheungJan@live.com>
    :license: MIT, see LICENSE for more details.
"""
import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

#SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

class BaseConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev key')

    DEBUG_TB_INTERCEPT_REDIRECTS = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    CKEDITOR_ENABLE = True
    CKEDITOR_FILE_UPLOADER = 'admin.upload_image'
    CKEDITOR_ENABLE_CSRF = True  # 启用CSRF保护
    CKEDITOR_HEIGHT = 400  # 编辑器高度

    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('Myblog Admin', 'MAIL_USERNAME')

    MYBLOG_EMAIL = os.getenv('MYBLOG_EMAIL')
    MYBLOG_POST_PER_PAGE = 10
    MYBLOG_MANAGE_POST_PER_PAGE = 15
    MYBLOG_COMMENT_PER_PAGE = 15
    #('THEME NAME','display name')
    MYBLOG_THEMES = {'perfect_blue':'Perfect Blue','black_swan':'Black Swan'}
    MYBLOG_SLOW_QUERY_THRESHOLD = 1

    MYBLOG_UPLOAD_PATH = os.path.join(basedir,'uploads')
    MYBLOG_ALLOWED_IMAGE_EXTENSIONS = {'png','jpg','jpeg','gif'}

class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir,'data-dev.db')

class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL',prefix + os.path.join(basedir,'data.db'))    
    
config = {
    'development':DevelopmentConfig,
    'testing':TestingConfig,
    'production':ProductionConfig
}
    
    
    