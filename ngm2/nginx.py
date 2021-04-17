import htpasswd
import os
import shutil
import subprocess
import pathlib

from datetime import date

from . import acme
from . import utils

def install_default():
	"""Override default.conf with ngm2 compatible settings"""
	acme_challenge = pathlib.Path("/var/www/.well-known/acme-challenge/") 	
	acme_challenge.mkdir(parents=True, exist_ok=True)

	utils.log_info("Creating new default file for nginx at /etc/nginx/conf.d/default.conf")
	utils.render_resource("conf/nginx.default", "/etc/nginx/conf.d/default.conf", {})

	if os.path.exists("/etc/nginx/sites-enabled/default"):
		utils.log_info("Unlinking old default file /etc/nginx/sites-enabled/default")
		os.unlink("/etc/nginx/sites-enabled/default")

def add_html(url:str, protected=False):
	"""Add nginx "location" configuration into domain's conf.d folder"""
	domain, path = utils.split_url(url)
	acme.ensure_domain(domain)
	
	web_root = pathlib.Path(f"/var/www/{domain}{path}")
	web_conf = pathlib.Path(f"/etc/nginx/conf.d/{domain}/{utils.to_dirname(path)}.conf")

	assert not web_root.exists(), f"Web root {web_root} already exists"
	assert not web_conf.exists(), f"{url} is already taken!"

	# create web roots
	web_root.mkdir(parents=True) # throws if folder already exists

	ctx = _standard_context(domain, path, protected)
	utils.render_resource("conf/nginx.path", web_conf, ctx)
	utils.log_info(f"You can place your html files into {web_root}")

def add_auth(url:str, username:str, password:str):
	domain, path = utils.split_url(url)
	acme.ensure_domain(domain)
	filepath = utils.authfile(domain, path)
	if os.path.exists(filepath):
		utils.log_info(f"Reusing authentication file {filepath}")
		return filepath
	pwfile = htpasswd.HtpasswdFile(filepath, create=htpasswd.options.create)
	pwdfile.update(username, password)
	pwfile.save()
	return filepath

def add_webdav(url:str, protected=False):
	"""Add nginx "location" configuration into domain's conf.d folder"""
	domain, path = utils.split_url(url)
	acme.ensure_domain(domain)
	assert is_safe(suffix), "Suffix cannot contain /"

	webdav_root = pathlib.Path(f"/var/webdav/{domain}{path}")
	webdav_conf = pathlib.Path(f"/etc/nginx/conf.d/{domain}/{utils.to_dirname(path)}.conf")

	assert not webdav_conf.exists(), f"{url} is already taken!"
	assert not webdav_root.exists(), f"webdav {url} already exists"

	webdav_root.mkdir(parents=True)
	shutil.chown(str(webdav_root), "www-data")
	ctx = _standard_context(domain, path, protected)
	utils.render_resource("conf/nginx.webdav", webdav_conf, ctx)
	utils.log_info(f"Your webdav folder is {webdav_root}")

def add_proxy(url:str, port:int, protected=False):
	domain, path = utils.split_url(url)
	acme.ensure_domain(domain)

	proxy_conf = pathlib.Path(f"/etc/nginx/conf.d/{domain}/{utils.to_dirname(path)}.conf")
	assert not proxy_conf.exists(), f"{url} is already taken!"

	ctx = _standard_context(domain, path, protected, port=port)
	utils.render_resource("conf/nginx.webdav", proxy_conf, ctx)

def apply():
	"""Apply settings by first checking them using `nginx -t` and then reloading nginx"""
	subprocess.run(["nginx", "-t"], check=True)
	subprocess.run(["systemctl", "reload", "nginx"], check=True)

def _standard_context(domain: str, path: str, protected:bool, **kwargs):
	ctx = {
		"path": path,
		"domain": domain
	}
	ctx.update(**kwargs)
	if protected:
		ctx.update(authfile=utils.find_authfile(domain, path))
	return ctx
