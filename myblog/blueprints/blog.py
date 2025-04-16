"""
    :author: CheungJan (CJ)
    :url: http://cheungjan.com
    :copyright: ©2025 Cheung Jan <CheungJan@live.com>
    :license: MIT, see LICENSE for more details.
"""
from flask import render_template, request, url_for, flash, redirect, current_app, Blueprint,abort,make_response
from flask_login import current_user
from myblog.emails import send_new_comment_email, send_new_reply_email
from myblog.extensions import db
from myblog.forms import CommentForm,AdminCommentForm
from myblog.models import Post,Comment,Category
from myblog.utils import redirect_back

blog_bp = Blueprint('blog', __name__)

@blog_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)#从查询字符串获取页码
    per_page = current_app.config['MYBLOG_POST_PER_PAGE']#每页显示的文章数量
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=per_page)#分页对象
    posts = pagination.items #当前页数的记录列表
    return render_template('blog/index.html', pagination=pagination, posts=posts)

@blog_bp.route('/about')
def about():
    return render_template('blog/about.html')

@blog_bp.route('/category/<int:category_id>')
def show_category(category_id):
    # 获取分类对象，如果不存在返回404
    category = Category.query.get_or_404(category_id)
    # 分页参数设置，与首页类似
    page = request.args.get('page', 1, type=int)
    # 每页显示的文章数量
    per_page = current_app.config['MYBLOG_POST_PER_PAGE']
    # 使用with_parent()方法获取分类下的所有文章
    pagination = Post.query.with_parent(category).order_by(Post.timestamp.desc()).paginate(page=page, per_page=per_page)
    # 获取文章列表
    posts = pagination.items
    # 渲染分类页面
    return render_template('blog/category.html', pagination=pagination, posts=posts, category=category)

@blog_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
    # 获取文章对象，如果不存在返回404
    post = Post.query.get_or_404(post_id)
    
    # 评论分页
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MYBLOG_COMMENT_PER_PAGE']
    # 注意这里改为按时间正序排序，与 bluelog 保持一致
    pagination = Comment.query.with_parent(post).filter_by(reviewed=True).order_by(Comment.timestamp.desc()).paginate(page=page, per_page=per_page)
    comments = pagination.items

    # 处理评论表单
    if current_user.is_authenticated:
        form = AdminCommentForm()
        form.author.data = current_user.name
        form.email.data = current_app.config['MYBLOG_EMAIL']
        form.site.data = url_for('.index')
        from_admin = True
        reviewed = True
    else:
        form = CommentForm()
        from_admin = False
        reviewed = False

    # 使用 request.method 和 form.validate() 进行验证
    if request.method == 'POST' and form.validate():
        author = form.author.data
        email = form.email.data
        site = form.site.data
        body = form.body.data
        comment = Comment(
            author=author, 
            email=email, 
            site=site, 
            body=body,
            from_admin=from_admin, 
            post=post, 
            reviewed=reviewed
        )
        
        # 处理回复评论
        replied_id = request.args.get('reply')
        if replied_id:
            replied_comment = Comment.query.get_or_404(replied_id)
            comment.replied = replied_comment
            send_new_reply_email(replied_comment)
            
        # 保存评论
        db.session.add(comment)
        db.session.commit()
        
        # 发送通知
        if current_user.is_authenticated:
            flash('评论已发布。', 'success')
        else:
            flash('感谢您的评论，审核通过后将会显示。', 'info')
            send_new_comment_email(post)  # 发送邮件通知管理员
            
        return redirect(url_for('.show_post', post_id=post_id))
        
    return render_template('blog/post.html', post=post, pagination=pagination, form=form, comments=comments)
    
@blog_bp.route('/reply/comment/<int:comment_id>')   
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if not comment.post.can_comment:
        flash('Comment is disabled.', 'warning')
        return redirect(url_for('.show_post', post_id=comment.post.id))
    return redirect(
        url_for('.show_post', post_id=comment.post_id, reply=comment_id, author=comment.author) + '#comment-form')
        
@blog_bp.route('/change-theme/<theme_name>')
def change_theme(theme_name):
    if theme_name not in current_app.config['MYBLOG_THEMES'].keys():
        abort(404)

    response = make_response(redirect_back())
    response.set_cookie('theme', theme_name,max_age=30*24*60*60)
    return response
