"""
    :author: CheungJan (CJ)
    :url: http://cheungjan.com
    :copyright: ©2025 Cheung Jan <CheungJan@live.com>
    :license: MIT, see LICENSE for more details.
"""
from threading import Thread
from flask import url_for,current_app
from flask_mail import Message
from myblog.extensions import mail

def _send_async_mail(app,message):
    with app.app_context():
        mail.send(message)

def send_mail(subject,to,html):
    # 直接使用 current_app
    message = Message(subject,recipients=[to],html=html)
    thr = Thread(target=_send_async_mail,args=(current_app._get_current_object(),message))
    thr.start()
    return thr

def send_new_comment_email(post):
    post_url = url_for('blog.show_post',post_id=post.id,external=True) + '#comments'
    send_mail(subject='New comment',to=current_app.config['MYBLOG_EMAIL'],
              html='<p>New comment on post <i>%s</i>,click the link below to check:</p>'
              '<p><a href="%s">%s</a></p>'
              '<p><small style="color: #868e96">Do not reply this email.</small></p>'
              % (post.title, post_url, post_url))

def send_new_reply_email(comment):
    post_url = url_for('blog.show_post',post_id=comment.post_id,_external=True) + '#comments'
    send_mail(subject='New reply',to=comment.email,
              html='<p>New reply for the comment you left in post <i>%s</i>, click the link below to check: </p>'
              '<p><a href="%s">%s</a></p>'
              '<p><small style="color: #868e96">Do not reply this email.</small></p>'
              % (comment.post.title, post_url, post_url))
              
    
    