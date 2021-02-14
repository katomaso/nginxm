import sys
import os

from . import conf
from . import acme

__usage__ = f"""Usage: nginxm COMMAND options

COMMANDS with options:

	add-domain <domain>
	add-path <domain> <path>
	add-webdav <domain> <path> <username> <password>

nginxm command must be run as root. It modifies nginx's conf.d
and writes to /etc/ssl and creates folders under /var/www/. It
also sets systemd timers for domain certificates renewals.

Some parts of this app can be modified using env vars:

	ACME_URL to change for example for staging environment https://acme-staging-v02.api.letsencrypt.org/directory
	ACME_KEY location where ACME account key is/will be stored; default: {acme.ACME_KEY}
	ACME_CHALLENGE location where the challenges should be stored to be served by nginx; default: {acme.ACME_CHALLENGE}
"""

# main function must be here because of setuptools entrypoint
# otherwise the content of main() would be simply in the file
def main() -> int:
	args = sys.argv[1:]
	if len(args) == 0 or "help" in args:
		print(__usage__, file=sys.stderr)
		return 0
	if "ACME_URL" in os.environ:
		acme.ACME_URL = os.environ["ACME_URL"]
	if "ACME_KEY" in os.environ:
		acme.ACME_KEY = os.environ["ACME_KEY"]
	if "ACME_CHALLENGE" in os.environ:
		acme.ACME_CHALLENGE = os.environ["ACME_CHALLENGE"]
	cmd = args[0]
	if cmd == "add-domain":
		domain, = check_args(args, 1)
		acme.add_domain(domain)
	if cmd == "renew-domain":
		domain, = check_args(args, 1)
		acme.renew_domain(domain)
	if cmd == "add-path":
		domain, path = check_args(args, 2)
		conf.add_path(domain, path)
	if cmd == "add-webdav":
		domain, path, username, password = check_args(args, 4)
		conf.add_webdav(domain, path, username, password)
	return 0

def check_args(args: list[str], n: int) -> tuple[str]:
	if len(args) < n+1:
		print("Not enough arguments for " + args[0], file=sys.stderr)
		print(__usage__, file=sys.stderr)
		sys.exit(1)
	return args[1:1+n+1]

if __name__ == "__main__":
	sys.exit(main())