"""
    :author: CheungJan (CJ)
    :url: http://cheungjan.com
    :copyright: ©2025 Cheung Jan <CheungJan@live.com>
    :license: MIT, see LICENSE for more details.
"""
from myblog.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Admin(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True) #主键字段
    username = db.Column(db.String(20)) #用户姓名
    password_hash = db.Column(db.String(128)) #密码散列值
    blog_title = db.Column(db.String(60)) #博客标题
    blog_sub_title = db.Column(db.String(100)) #博客副标题
    name = db.Column(db.String(30)) #作者姓名
    about = db.Column(db.Text) #关于

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

class Category(db.Model):
    id = db.Column(db.Integer,primary_key=True) #主键字段
    name = db.Column(db.String(30),unique=True) #分类名称
    posts = db.relationship('Post',back_populates='category') #文章

    def delete(self):
        default_category = Category.query.get(1)
        posts = self.posts[:]
        for post in posts:
            post.category = default_category
        db.session.delete(self)
        db.session.commit()

class Post(db.Model):
    id = db.Column(db.Integer,primary_key=True) #主键字段
    title=db.Column(db.String(60)) #标题
    body = db.Column(db.Text) #内容
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True) #时间戳
    can_comment = db.Column(db.Boolean, default=True) #是否允许评论

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    category = db.relationship('Category', back_populates='posts')
    comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan')

class Comment(db.Model):
    id = db.Column(db.Integer,primary_key=True) #主键字段
    author = db.Column(db.String(30)) #作者
    email = db.Column(db.String(254)) #邮箱
    site = db.Column(db.String(255)) #网站
    body = db.Column(db.Text) #内容
    from_admin = db.Column(db.Boolean, default=False) #是否来自管理员
    reviewed = db.Column(db.Boolean, default=False) #是否审核
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True) # 评论时间
    
    replied_id = db.Column(db.Integer, db.ForeignKey('comment.id')) # 回复的评论ID
    post_id = db.Column(db.Integer, db.ForeignKey('post.id')) # 所属文章ID

    post = db.relationship('Post', back_populates='comments') # 与文章的关系
    replies = db.relationship('Comment', back_populates='replied', cascade='all, delete-orphan')  # 回复列表   
    replied = db.relationship('Comment', back_populates='replies', remote_side=[id])  # 被回复的评论

class Link(db.Model):
    id = db.Column(db.Integer,primary_key=True) #主键字段
    name = db.Column(db.String(30)) #链接名称
    url = db.Column(db.String(255)) #链接地址