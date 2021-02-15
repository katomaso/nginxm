import jinja2
import pkg_resources
import logging

logger = logging.getLogger("nginxm")

def render_resource(resource: str, target: str, context: dict):
	template = str(pkg_resources.resource_string("nginxm", resource))
	content = jinja2.Template(template).render(context)
	with open(target, "wt") as target_file:
		target_file.write(target_content)

def log_info(msg: str):
	logger.info(msg)

def log_debug(msg: str):
	logger.debug(msg)

def log_level(level: str):
	logging.basicConfig(level=logging.DEBUG if level=="debug" else logging.INFO)