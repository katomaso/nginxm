import sys
import os

from . import nginx
from . import acme
from . import utils

from typing import List

__usage__ = f"""Usage: ngm2 COMMAND options

COMMANDS with options:

	init - run initially to set new "default" server config in nginx
	html <url>
	proxy <url> <port>
	webdav <url>
	add-auth <url or a filename> <username> [<password>]

ngm2 command must be run as root. It modifies nginx's conf.d
and writes to /etc/ssl and creates folders under /var/www/. It
also sets systemd timers for domain certificates renewals.

Some parts of this app can be modified using env vars:
	DEBUG set to any value to allow debugging output
	ACME_MOCK use unsecured domains and do not contact letsencrypt.com at all
	ACME_URL to change for example for staging environment https://acme-staging-v02.api.letsencrypt.org/directory
	ACME_KEY location where ACME account key is/will be stored; default: {acme.ACME_KEY}
	ACME_CHALLENGE location where the challenges should be stored to be served by nginx; default: {acme.ACME_CHALLENGE}
"""

kwargs_def = {
	"--use-auth": {"default": None, },
}

# main function must be here because of setuptools entrypoint
# otherwise the content of main() would be simply in the file
def main() -> int:
	args = sys.argv[1:]
	if len(args) == 0 or "help" in args or "--help" in args:
		print(__usage__, file=sys.stderr)
		return 0
	if "DEBUG" in os.environ:
		utils.log_level("debug")
	else:
		utils.log_level("info")
	# remove --parameters from the app's arguments and place them into `kwargs`
	kwargs = {}
	for key, vals in kwargs_def.items():
		if key in args:
			i = args.index(key)
			del args[i]
			if vals > 0:
				kwargs[key] = args.pop(i)
			else:
				kwargs[key] = True
	# inspect env var that modifies the program's execution
	if "ACME_URL" in os.environ:
		acme.ACME_URL = os.environ["ACME_URL"]
	if "ACME_KEY" in os.environ:
		acme.ACME_KEY = os.environ["ACME_KEY"]
	if "ACME_CHALLENGE" in os.environ:
		acme.ACME_CHALLENGE = os.environ["ACME_CHALLENGE"]
	if "ACME_MOCK" in os.environ:
		acme.ACME_MOCK = True
	cmd = args.pop(0)
	if cmd == "init":
		nginx.init()
	elif cmd == "add-domain":
		domain = get_args(args, 1)
		acme.add_domain(domain)
	elif cmd == "renew-domain":
		domain = get_args(args, 1)
		acme.renew_domain(domain)
	elif cmd == "remove-domain":
		domain = get_args(args, 1)
		acme.remove_domain(domain)
	elif cmd == "html":
		url = get_args(args, 1)
		nginx.add_html(url, auth=kwargs.get('--use-auth'))
	elif cmd == "add-auth":
		if len(args) == 2:
			url, username, password = *get_args(args, 2), None
		else:
			url, username, password = get_args(args, 3)
		nginx.add_auth(url, username, password)
	elif cmd == "webdav":
		url = get_args(args, 1)
		nginx.add_webdav(url, auth=kwargs.get('--use-auth'))
	elif cmd == "proxy":
		url, port = get_args(args, 2)
		nginx.add_proxy(url, port, auth=kwargs.get('--use-auth'))
	else:
		print(__usage__, file=sys.stderr)
		return 1
	return 0

def get_args(args, n: int):
	if n == 1 and len(args) >= 1:
		return args[0]
	if len(args) < n:
		print("Not enough arguments", file=sys.stderr)
		print(__usage__, file=sys.stderr)
		sys.exit(1)
	return args[:n]

if __name__ == "__main__":
	sys.exit(main())