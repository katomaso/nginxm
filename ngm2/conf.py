import htpasswd
import os
import shutil
import subprocess

from datetime import date

from . import acme
from . import utils

def add_path(domain: str, path: str, protected=False):
	# create web roots
	os.makedirs(f"/var/www/{domain}{path}") # throws if folder already exists
	shutil.chown(f"/var/www/{domain}{path}", "www-data")

	"""Add nginx "location" configuration into domain's conf.d folder"""
	ctx = _standard_context(domain, path, protected)
	utils.render_resource("conf/nginx.path", f"/etc/nginx/conf.d/{domain}/{utils.to_dirname(path)}.conf", ctx)

	subprocess.run(["nginx", "-t"], check=True)
	subprocess.run(["systemctl", "reload", "nginx"], check=True)

def add_auth(domain: str, path: str, username:str, password:str):
	filepath = utils.authfile(domain, path)
	if os.path.exists(filepath):
		utils.log_info(f"Reusing authentication file {filepath}")
		return filepath
	pwfile = htpasswd.HtpasswdFile(filepath, create=htpasswd.options.create)
	pwdfile.update(username, password)
	pwfile.save()
	return filepath

def add_webdav(domain: str, path: str, suffix="webdav", protected=False):
	"""Add nginx "location" configuration into domain's conf.d folder"""
	path_dirname = utils.to_dirname(path)
	assert is_safe(suffix), "Suffix cannot contain /"

	os.makedirs(f"/var/webdav/{domain}{path}") # throws if folder already exists
	shutil.chown(f"/var/webdav/{domain}{path}", "www-data")
	ctx = _standard_context(domain, path, protected)
	utils.render_resource("conf/nginx.webdav", f"/etc/nginx/conf.d/{domain}/{path_dirname}-{suffix}.conf", ctx)

def add_proxy(domain: str, path: str, suffix:str, port:int, protected=False):
	"""Add nginx "location" configuration into domain's conf.d folder"""
	fullpath = path + "" if not suffix else f"/{suffix}".replace("//", "/")
	ctx = _standard_context(domain, path, protected)
	ctx.update(port=port)
	utils.render_resource("conf/nginx.webdav", f"/etc/nginx/conf.d/{domain}/{utils.to_dirname(fullpath)}.conf", ctx)

def _standard_context(domain: str, path: str, protected:bool):
	ctx = {
		"path": path,
		"domain": domain
	}
	if protected:
		ctx.update(authfile=utils.find_authfile(domain, path))
	return ctx
