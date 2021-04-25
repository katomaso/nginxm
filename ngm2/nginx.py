import htpasswd
import os
import shutil
import subprocess
import pathlib

from datetime import date

from . import acme
from . import utils

WEB_ROOT = pathlib.Path("/var/www/")
DAV_ROOT = pathlib.Path("/var/dav/")
AUTH_ROOT = pathlib.Path("/var/auth/")

def init():
	"""Prepare directories and override default.conf with ngm2 compatible settings"""
	acme_challenge = pathlib.Path("/var/www/.well-known/acme-challenge/")
	acme_challenge.mkdir(parents=True, exist_ok=True)

	utils.log_info("Creating new default file for nginx at /etc/nginx/conf.d/default.conf")
	utils.render_resource("conf/nginx.default", "/etc/nginx/conf.d/default.conf", {})

	if os.path.exists("/etc/nginx/sites-enabled/default"):
		utils.log_info("Unlinking old default file /etc/nginx/sites-enabled/default")
		os.unlink("/etc/nginx/sites-enabled/default")

def add_html(url:str, auth=False):
	"""Add nginx "location" configuration into domain's conf.d folder"""
	domain, path = utils.split_url(url)
	acme.ensure_domain(domain)

	web_root = WEB_ROOT / domain / utils.to_dirname(path)
	web_conf = pathlib.Path(f"/etc/nginx/conf.d/{domain}/{utils.to_dirname(path)}.conf")

	assert not web_root.exists(), f"Web root {web_root} already exists"
	assert not web_conf.exists(), f"{url} is already taken!"

	# create web roots
	web_root.mkdir(parents=True) # throws if folder already exists

	ctx = _standard_context(domain, path, auth, root=web_root)
	utils.render_resource("conf/nginx.html", web_conf, ctx)
	utils.log_info(f"You can place your html files into {web_root}")

def add_auth(url:str, username:str, password:str):
	domain, path = utils.split_url(url)
	acme.ensure_domain(domain)
	authfile = _authfile(url)
	authfile.parent.mkdir(parents=True, exist_ok=True)
	authfile.touch()
	if password is None:
		password = input("Password: ")
	with htpasswd.Basic(authfile) as authdb:
		if username in authdb:
			utils.log_info(f"User {username} already exists - updating their password")
			authdb.change_password(username, password)
		else:
			utils.log_info(f"User {username} added to {url} authentication file")
			authdb.add(username, password)

def add_webdav(url:str, auth=False):
	"""Add nginx "location" configuration into domain's conf.d folder"""
	domain, path = utils.split_url(url)
	acme.ensure_domain(domain)

	webdav_root = DAV_ROOT / domain / utils.to_dirname(path)
	webdav_conf = pathlib.Path(f"/etc/nginx/conf.d/{domain}/{utils.to_dirname(path)}.conf")

	assert not webdav_conf.exists(), f"{url} is already taken!"
	assert not webdav_root.exists(), f"webdav {url} already exists"

	webdav_root.mkdir(parents=True)
	shutil.chown(str(webdav_root), "www-data")
	ctx = _standard_context(domain, path, auth, root=webdav_root)
	utils.render_resource("conf/nginx.webdav", webdav_conf, ctx)
	utils.log_info(f"Your new webdav folder is {webdav_root}")

def add_proxy(url:str, port:int, auth=False):
	domain, path = utils.split_url(url)
	acme.ensure_domain(domain)

	proxy_conf = pathlib.Path(f"/etc/nginx/conf.d/{domain}/{utils.to_dirname(path)}.conf")
	assert not proxy_conf.exists(), f"{url} is already taken!"

	ctx = _standard_context(domain, path, auth, port=port)
	utils.render_resource("conf/nginx.proxy", proxy_conf, ctx)
	utils.log_info(f"Path {path} now proxies localhost:{port}")

def apply():
	"""Apply settings by first checking them using `nginx -t` and then reloading nginx"""
	subprocess.run(["nginx", "-t"], check=True)
	subprocess.run(["systemctl", "reload", "nginx"], check=True)

def _standard_context(domain: str, path: str, auth:str, **kwargs):
	ctx = {
		"path": path,
		"domain": domain,
		"authfile": utils.must_exist(_authfile(auth))
	}
	ctx.update(**kwargs)
	return ctx

def _authfile(auth):
	if auth is None:
		return None
	return AUTH_ROOT / utils.to_dirname(auth)