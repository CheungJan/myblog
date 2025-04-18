"""
    :author: CheungJan (CJ)
    :url: http://cheungjan.com
    :copyright: © 2025 Cheung Jan <CheungJan@live.com>
    :license: MIT, see LICENSE for more details.
"""
import logging
import os
from logging.handlers import SMTPHandler, RotatingFileHandler

import click
from flask import Flask,render_template,request
from flask_login import current_user
from flask_sqlalchemy import get_debug_queries
from flask_wtf.csrf import CSRFError

from myblog.blueprints.admin import admin_bp
from myblog.blueprints.auth import auth_bp
from myblog.blueprints.blog import blog_bp
from myblog.extensions import bootstrap,db,login_manager,csrf,ckeditor,mail,moment,migrate,toolbar
from myblog.models import Admin,Category,Post,Comment,Link
from myblog.settings import config

# 基础目录 basedir=E:\project\Escort_management_system\flask_demo\myblog
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))   

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    register_logging(app) # 注册日志处理器
    register_extensions(app) # 注册扩展
    register_blueprints(app) # 注册蓝图
    register_commands(app) # 注册自定义shell命令
    register_errors(app) # 注册错误处理函数
    register_shell_context(app)  # 注册 shell 上下文处理函数
    register_template_context(app) # 注册模板上下文处理函数
    register_request_handlers(app) # 注册请求处理器

    return app


def register_logging(app):
    class RequestFormatter(logging.Formatter):

        def format(self, record):
            record.url = request.url
            record.remote_addr = request.remote_addr
            return super(RequestFormatter, self).format(record)

    request_formatter = RequestFormatter(
            '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
            '%(levelname)s in %(module)s: %(message)s'
    )

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s -%(message)s')

    file_handler = RotatingFileHandler(os.path.join(basedir,'logs/myblog.log'),
                                             maxBytes=10*1024*1024,backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    mail_handler = SMTPHandler(
            mailhost=app.config['MAIL_SERVER'],
            fromaddr=app.config['MAIL_USERNAME'],
            toaddrs=['ADMIN_EMAIL'],
            subject='MyBlog Application Error',
            credentials=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']))
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(request_formatter)

    if not app.debug:
        app.logger.addHandler(mail_handler)
        app.logger.addHandler(file_handler)
        
def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    migrate.init_app(app, db)
    # toolbar.init_app(app)  # 暂时禁用debug toolbar以解决跨盘符问题

def register_blueprints(app): 
    app.register_blueprint(blog_bp)         
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')

def register_shell_context(app):
    @app.shell_context_processor
    def make_context():
        return dict(db=db, Admin=Admin, Category=Category, Post=Post, Comment=Comment, Link=Link)

def register_template_context(app):
    @app.context_processor
    def make_template_context():
        admin=Admin.query.first()
        categories=Category.query.all()
        links=Link.query.all()
        if current_user.is_authenticated:
            unread_comments = Comment.query.filter_by(reviewed=False).count()
        else:
            unread_comments = None
        return dict(admin=admin, categories=categories, links=links, unread_comments=unread_comments)

def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/csrf_error.html', e=e), 400

def register_commands(app):
    @app.cli.command('initdb')
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initialize dataase."""
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')
    
    @app.cli.command()
    @click.option('--username', prompt=True, help='The username used to login.')
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
    def init(username, password):        
        """Building Bluelog,just for you."""
        
        click.echo('Initializing the database...')
        db.create_all()

        admin = Admin.query.first()
        if admin is not None:
            click.echo('The administrator already exists,updating...')
            admin.username = username
            admin.set_password(password)
        else:
            click.echo('Creating the temporary administrator account...')
            admin = Admin(
                username=username,
                blog_title='My Blog',
                blog_sub_title="No, I'm the real thing.",
                name='Admin',
                about='Anything about you.'
            )
            admin.set_password(password)
            db.session.add(admin)
        
        category = Category.query.first()
        if category is None:
            click.echo('Creating the default category...')
            category = Category(name='Default')
            db.session.add(category)
        
        db.session.commit()
        click.echo('Done.')

    @app.cli.command()
    @click.option('--category', default=10, help='Quantity of categories, default is 10.')
    @click.option('--post', default=50, help='Quantity of posts, default is 50.')
    @click.option('--comment', default=500, help='Quantity of comments, default is 500.')
    def forge(category, post, comment):
        """Generate fake data."""
        from myblog.fakes import fake_admin, fake_categories, fake_posts, fake_comments, fake_links
        
        db.drop_all()
        db.create_all()
        
        click.echo('Initializing the database...')
        fake_admin()

        click.echo('Generating %d categories...' % category)
        fake_categories(category)
        
        click.echo('Generating %d posts...' % post)
        fake_posts(post)
        
        click.echo('Generating %d comments...' % comment)
        fake_comments(comment)

        click.echo('Generating links...')
        fake_links()

        click.echo('Done.')
         
def register_request_handlers(app):
    @app.after_request
    def query_time_stat(request):
        for q in get_debug_queries():
            if q.duration >= app.config['MYBLOG_SLOW_QUERY_THRESHOLD']:
                app.logger.warning(
                    'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s'
                    % (q.statement, str(q.parameters), q.duration, str(q.context))
                )
        return request

# 在文件末尾添加
# app = create_app('development')