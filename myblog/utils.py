"""
    :author: CheungJan (CJ)
    :url: http://cheungjan.com
    :copyright: ©2025 Cheung Jan <CheungJan@live.com>
    :license: MIT, see LICENSE for more details.
"""
try:
    from urllib.parse import urlparse,urljoin
except ImportError:
    from urllib.parse import urlparse,urljoin

from flask import request,redirect,url_for,current_app  

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def redirect_back(default='index', **kwargs):
    for target in (request.args.get('next'), request.args.get('redirect_to'), request.referrer):
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['MYBLOG_ALLOWED_IMAGE_EXTENSIONS']