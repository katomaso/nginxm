import sys
import os

from . import nginx
from . import acme
from . import utils

from typing import List

__usage__ = f"""Usage: ngm2 COMMAND options

COMMANDS with options:

	install - run initially to set new "default" server config in nginx
	html <url>
	proxy <url> <port>
	webdav <url> <username> <password>

ngm2 command must be run as root. It modifies nginx's conf.d
and writes to /etc/ssl and creates folders under /var/www/. It
also sets systemd timers for domain certificates renewals.

Some parts of this app can be modified using env vars:
	DEBUG set to any value to allow debugging output
	ACME_URL to change for example for staging environment https://acme-staging-v02.api.letsencrypt.org/directory
	ACME_KEY location where ACME account key is/will be stored; default: {acme.ACME_KEY}
	ACME_CHALLENGE location where the challenges should be stored to be served by nginx; default: {acme.ACME_CHALLENGE}
"""

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

	if "ACME_URL" in os.environ:
		acme.ACME_URL = os.environ["ACME_URL"]
	if "ACME_KEY" in os.environ:
		acme.ACME_KEY = os.environ["ACME_KEY"]
	if "ACME_CHALLENGE" in os.environ:
		acme.ACME_CHALLENGE = os.environ["ACME_CHALLENGE"]
	if "ACME_MOCK" in os.environ:
		acme.ACME_MOCK = True
	cmd = args[0]
	if cmd == "install":
		nginx.install_default()
	elif cmd == "add-domain":
		domain, = check_args(args, 1)
		acme.add_domain(domain)
	elif cmd == "renew-domain":
		domain, = check_args(args, 1)
		acme.renew_domain(domain)
	elif cmd == "remove-domain":
		domain, = check_args(args, 1)
		acme.remove_domain(domain)
	elif cmd == "html":
		url, = check_args(args, 1)
		nginx.add_html(url, protected=check_protected(args))
	elif cmd == "add-auth":
		url, username, password = check_args(args, 3)
		nginx.add_auth(url, username, password)
	elif cmd == "webdav":
		url, = check_args(args, 1)
		nginx.add_webdav(url, protected=check_protected(args))
	elif cmd == "proxy":
		url, port = check_args(args, 2)
		nginx.add_proxy(url, port, protected=check_protected(args))
	else:
		print(__usage__, file=sys.stderr)
		return 1
	return 0

def check_args(args, n: int):
	if len(args) < n+1:
		print("Not enough arguments for " + args[0], file=sys.stderr)
		print(__usage__, file=sys.stderr)
		sys.exit(1)
	return args[1:1+n+1]

def check_protected(args: List[str]):
	return "--protected" in args

if __name__ == "__main__":
	sys.exit(main())