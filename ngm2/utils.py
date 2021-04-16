import jinja2
import pkg_resources
import logging
import os.path

logger = logging.getLogger("ngm2")

def render_resource(resource: str, target: str, context: dict):
	template = pkg_resources.resource_string("ngm2", resource).decode('utf-8')
	content = jinja2.Template(template).render(context)
	with open(target, "wt") as target_file:
		target_file.write(content)

def must_exist(path: str, msg=None):
	if not os.path.exists(path):
		if msg is None:
			msg = f"File {path} does not exist"
		raise IOError(msg)
	return path

AUTH_ROOT = pathlib.Path("/var/authfile/")
def authfile(domain: str, path: str):
	return AUTH_ROOT / domain / utils.to_dirname(path)

def find_authfile(domain, path):
	find_root = AUTH_ROOT / domain
	p = path.strip("/")
	while p:
		authfile = find_root / utils.to_dirname(p)
		if authfile.exists():
			return str(authfile)
		last_slash_index = p.rfind("/")
		if last_slash_index < 0:
			authfile = find_root / utils.to_dirname("/")
			if not authfile.exists():
				raise IOError(f"Authentication file for {domain}{path} doesn't exist; run 'ngm2 add-auth {domain} {path} <username> <password>'")
			return str(authfile)
		p = p[:last_slash_index]

def log_info(msg: str):
	logger.info(msg)

def log_debug(msg: str):
	logger.debug(msg)

def log_level(level: str):
	logging.basicConfig(level=logging.DEBUG if level=="debug" else logging.INFO)

def to_dirname(path:str) -> str:
	"""Turn a webpath into usable directory name by replacing '/' and having non-empty result"""
	return (path.strip("/").replace('/', '-') if path != "/" else "default")

def is_safe(s:str):
	return "/" not in s