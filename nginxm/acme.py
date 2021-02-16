import acme_tiny
import jinja2
import os
import os.path
import pkg_resources
import shutil
import subprocess

from datetime import date

from . import utils

ACME_URL = acme_tiny.DEFAULT_DIRECTORY_URL
ACME_KEY = "/etc/ssl/acme/account.key"
ACME_CHALLENGE = "/var/www/.well-known/acme-challenge"

def exist_domain(domain: str) -> bool :
	crt_link = f"/etc/ssl/private/{domain}.crt"
	domain_conf = f"/etc/nginx/conf.d/{domain}.conf"
	return os.path.exists(crt_link) and os.path.exists(domain_conf)

def add_domain(domain: str):
	"""Create nginx conf and domain certificate and systemd renewal timer""" 
	if domain.startswith("http"):
		raise ValueError("Domain must not contain schema (http[s])")
	if "/" in domain:
		raise ValueError("Domain must not contain path")

	assert os.path.isdir(ACME_CHALLENGE), f"Folder {ACME_CHALLENGE} must exist"

	key = f"/etc/ssl/acme/{domain}.key"
	csr = f"/etc/ssl/acme/{domain}.csr"
	crt = f"/etc/ssl/private/{domain}.crt"

	assert not os.path.exists(key), "Key for the domain already exist at " + key
	assert not os.path.exists(csr), "Signing request for the domain already exist at " + csr

	# create private key for the domain
	with open(key, "wb") as key_file:
		subprocess.run(["openssl", "genrsa", "4096"], stdout=key_file, check=True)
		utils.log_info("Created domain key " + key)

	# create a CSR for the domain
	with open(csr, "wb") as csr_file:
		subprocess.run(["openssl", 'req', '-new', '-sha256', '-key', key, '-subj', f'/CN={domain}'], stdout=csr_file, check=True)
		utils.log_info("Created request file " + csr)

	domain_folder = f"/etc/nginx/conf.d/{domain}"
	utils.render_resource("conf/nginx.conf", f"/etc/nginx/conf.d/{domain}.conf", {
		"DOMAIN_CRT": crt, "DOMAIN_KEY": key, "DOMAIN": domain})
	if not os.path.exists(domain_folder):
		os.mkdir(domain_folder)
	utils.log_info("Added new nginx domain config " + domain_folder + ".conf")

	# generate signed certificate
	renew_domain(domain)

	# add domain renewal timer and start it right away
	if not os.path.exists("/etc/systemd/system/renew-domain@.service"):
		# install the template for certificate renewals
		utils.render_resource("conf/systemd.template", "/etc/systemd/system/renew-domain@.service", {
			"binary": shutil.which("nginxm")}) # installed as entry-point
	# create timer for the renewal if it was successful
	utils.render_resource("conf/systemd.timer", f"/etc/systemd/system/renew-domain@{domain}.timer", {})
	utils.log_info("Generated systemd timer " + f"/etc/systemd/system/renew-domain@{domain}.timer")

	subprocess.run(["systemctl", "enable", f"renew-domain@{domain}.timer"], check=True, capture_output=True)
	subprocess.run(["systemctl", "start", f"renew-domain@{domain}.timer"], check=True, capture_output=True)
	utils.log_info("Timer enabled and started")


def	renew_domain(domain: str):
	d = date.today()
	crt = f"/etc/ssl/acme/{domain}-{d.year}{d.month}{d.day}.crt"
	crt_link = f"/etc/ssl/private/{domain}.crt"

	# sign the request using acme_tiny
	crt_data = acme_tiny.get_crt(csr=csr, acme_dir=ACME_CHALLENGE, account_key=ACME_KEY)
	with open(crt, "wb") as crt_file:
		crt_file.write(crt_data)
	utils.log_info("Generated signed certificate " + crt)

	# update the symlink to point to newly generated file
	if os.path.exists(crt_link):
		os.unlink(crt_link)
	os.symlink(crt, crt_link)
	utils.log_info("Symlinked certificate to " + crt_link)

	subprocess.run(["nginx", "-t"], check=True)
	subprocess.run(["systemctl", "reload", "nginx"], check=True)
	utils.log_info("Nginx reloaded")