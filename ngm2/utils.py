import jinja2
import pkg_resources
import logging
import os.path
import pathlib
from typing import Union, List

logger = logging.getLogger("ngm2")

def render_resource(resource: str, target: Union[str,pathlib.Path], context: dict):
	template = pkg_resources.resource_string("ngm2", resource).decode('utf-8')
	content = jinja2.Template(template).render(context)
	with open(str(target), "wt") as target_file:
		target_file.write(content)

def must_exist(path: str, msg=None):
	if not path:
		return None
	if not os.path.exists(path):
		if msg is None:
			msg = f"File {path} does not exist"
		raise IOError(msg)
	return path

def log_info(msg: str):
	logger.info(msg)

def log_debug(msg: str):
	logger.debug(msg)

def log_level(level: str):
	logging.basicConfig(level=logging.DEBUG if level=="debug" else logging.INFO)

def to_dirname(path: str) -> str:
	"""Turn a webpath into usable directory name by replacing '/' and having non-empty result"""
	path = path.strip("/.")
	if path == "":
		return "default"
	return path.replace('/', '-')

def split_url(url: str):
	assert not url.startswith("http"), "URL must not contain protocol - just domain/path"
	index = url.find("/")
	if index < 0:
		return url, "/"
	return url[:index], url[index:]