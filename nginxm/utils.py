import jinja2
import pkg_resources

def render_resource(resource: str, target: str, context: dict):
	content = jinja2.Template(pkg_resources.resource_string("nginxm", resource)).render(context)
	with open(target, "wt") as target_file:
		target_file.write(target_content)