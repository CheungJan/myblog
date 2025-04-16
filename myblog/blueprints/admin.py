"""
    :author: CheungJan (CJ)
    :url: http://cheungjan.com
    :copyright: ©2025 Cheung Jan <CheungJan@live.com>
    :license: MIT, see LICENSE for more details.
"""
import os

from flask import render_template, flash, redirect, url_for, request, current_app, Blueprint, send_from_directory, abort
from werkzeug.utils import secure_filename
from markupsafe import Markup
from flask_login import login_required, current_user
from flask_ckeditor import upload_success, upload_fail

from myblog.extensions import db
from myblog.forms import SettingForm,PostForm,CategoryForm,LinkForm
from myblog.models import Post,Category,Comment,Link
from myblog.utils import redirect_back,allowed_file

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/settings',methods=['GET','POST'])
@login_required
def settings():
    form = SettingForm()
    if request.method == 'POST' and form.validate():
        current_user.name = form.name.data
        current_user.blog_title = form.blog_title.data
        current_user.blog_sub_title = form.blog_sub_title.data
        current_user.about = form.about.data
        db.session.commit()
        flash('Setting updated.', 'success')
        return redirect(url_for('blog.index'))
    form.name.data = current_user.name
    form.blog_title.data = current_user.blog_title
    form.blog_sub_title.data = current_user.blog_sub_title
    form.about.data = current_user.about
    return render_template('admin/settings.html', form=form)

@admin_bp.route('/post/manage')
@login_required
def manage_post():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=current_app.config['MYBLOG_MANAGE_POST_PER_PAGE'])
    posts = pagination.items
    return render_template('admin/manage_post.html', page=page, pagination=pagination, posts=posts)

@admin_bp.route('/post/new',methods=['GET','POST'])
@login_required
def new_post():
    form = PostForm()
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        category = Category.query.get(form.category.data)
        post = Post(title=title, body=body, category=category)
        # same with:
        # category_id = form.category.data
        # post = Post(title=title, body=body, category_id=category_id)
        db.session.add(post)
        db.session.commit()
        flash('Post created.', 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))
    return render_template('admin/new_post.html', form=form)

@admin_bp.route('/post/<int:post_id>/edit',methods=['GET','POST'])
@login_required
def edit_post(post_id):
    form = PostForm()
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST' and form.validate():
        post.title = form.title.data
        post.body = form.body.data
        post.category = Category.query.get(form.category.data)
        db.session.commit()
        flash('Post updated.', 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    form.category.data = post.category.id
    return render_template('admin/edit_post.html', form=form)

@admin_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'success')
    return redirect_back()

@admin_bp.route('post/<int:post_id>/set-comment', methods=['POST'])
@login_required
def set_comment(post_id):
    post = Post.query.get_or_404(post_id)
    if post.can_comment:
        post.can_comment = False
        flash('Comment disabled.', 'success')
    else:
        post.can_comment = True
        flash('Comment enabled.', 'success')
    db.session.commit()
    return redirect_back()

@admin_bp.route('/comment/manage')
@login_required
def manage_comment():
    filter_rule = request.args.get('filter', 'all')  # 'all', 'unreviewed', 'admin'
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MYBLOG_COMMENT_PER_PAGE']
    if filter_rule == 'unread':
        filtered_comments = Comment.query.filter_by(reviewed=False)
    elif filter_rule == 'admin':
        filtered_comments = Comment.query.filter_by(from_admin=True)
    else:
        filtered_comments = Comment.query

    pagination = filtered_comments.order_by(Comment.timestamp.desc()).paginate(page=page, per_page=per_page)
    comments = pagination.items
    return render_template('admin/manage_comment.html', comments=comments, pagination=pagination)

@admin_bp.route('/comment/<int:comment_id>/approve', methods=['POST'])
@login_required
def approve_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.reviewed = True
    db.session.commit()
    flash('Comment published.', 'success')
    return redirect_back()

@admin_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'success')
    return redirect_back()

@admin_bp.route('/category/manage')
@login_required
def manage_category():
    return render_template('admin/manage_category.html')

@admin_bp.route('/category/new', methods=['GET', 'POST'])
@login_required
def new_category():
    form = CategoryForm()
    if request.method == 'POST' and form.validate():
        name = form.name.data
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        flash('Category created.', 'success')
        return redirect(url_for('.manage_category'))
    return render_template('admin/new_category.html', form=form)

@admin_bp.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    form = CategoryForm()
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        flash('You can not edit the default category.', 'warning')
        return redirect(url_for('.blog.index'))
    if request.method == 'POST' and form.validate():
        category.name = form.name.data
        db.session.commit()
        flash('Category updated.', 'success')
        return redirect(url_for('.manage_category'))

    form.name.data = category.name
    return render_template('admin/edit_category.html', form=form)

@admin_bp.route('/category/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        flash('You can not delete the default category.', 'warning')
        return redirect(url_for('blog.index'))
    category.delete()
    flash('Category deleted.', 'success')
    return redirect(url_for('.manage_category'))

@admin_bp.route('/link/manage')
@login_required
def manage_link():
    return render_template('admin/manage_link.html')

@admin_bp.route('/link/new', methods=['GET', 'POST'])
@login_required
def new_link():
    form = LinkForm()
    if request.method == 'POST' and form.validate():
        name = form.name.data
        link = Link(name=name, url=form.url.data)
        db.session.add(link)
        db.session.commit()
        flash('Link created.', 'success')
        return redirect(url_for('.manage_link'))
    return render_template('admin/new_link.html', form=form)

@admin_bp.route('/link/<int:link_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_link(link_id):
    form = LinkForm()
    link = Link.query.get_or_404(link_id)
    if request.method == 'POST' and form.validate():
        link.name = form.name.data
        link.url = form.url.data
        db.session.commit()
        flash('Link updated.', 'success')
        return redirect(url_for('.manage_link'))
    form.name.data = link.name
    form.url.data = link.url
    return render_template('admin/edit_link.html', form=form)

@admin_bp.route('/link/<int:link_id>/delete', methods=['POST'])
@login_required
def delete_link(link_id):
    link = Link.query.get_or_404(link_id)
    link.delete()
    flash('Link deleted.', 'success')
    return redirect(url_for('.manage_link'))

@admin_bp.route('/uploads/<path:filename>')
def get_image(filename):
    try:
        return send_from_directory(current_app.config['MYBLOG_UPLOAD_PATH'], filename)
    except Exception as e:
        current_app.logger.error(f'图片加载失败: {str(e)}')
        abort(404)


@admin_bp.route('/uploads',methods=['POST'])
@login_required
def upload_image():
    f = request.files.get('upload')
    if not f:
        return upload_fail('No file uploaded!')
    if not allowed_file(f.filename):
        return upload_fail('只允许上传图片文件！')
    # 确保上传目录存在
    upload_path = current_app.config['MYBLOG_UPLOAD_PATH']
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    # 生成安全的文件名
    filename = secure_filename(f.filename)
    try:
        f.save(os.path.join(upload_path, filename))
        url = url_for('.get_image', filename=filename)
        return upload_success(url, filename)
    except Exception as e:
        current_app.logger.error(f'上传失败: {str(e)}')
        return upload_fail('上传失败，请重试！')

