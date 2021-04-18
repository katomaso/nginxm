# ngm2

Simple management tool for nginx's virtual servers with automatic SSL certificates.
It uses systemd timers for renewals of the certificates.

## Configuration

Install by `pip install ngm2`. Now you have `ngm2` binary available.

Ngm2 supposes that HTTP traffic is handled by your current nginx's config. Ngm2 create handlers only for HTTPS trafic. Therefore your HTTP configuration should look as following. If you want
ngm2 to handle your nginx configuration exclusively then use `ngm2 install` to use exactly this as the default config.

```
server {
	listen 80 default_server;
	listen [::]:80 default_server;

	# catch all hostnames
	server_name _;

	# support letsencrypt ACME protocol
	location /.well-known/acme-challenge/ {
		root /var/www/;
	}

	# redirect any traffic (excluding ACME) to HTTPS
	location / {
		return 301 https://$host$request_uri;
	}
}
```

## Usage

### CLI

`ngm2` is a binary that creates configs, folders, keys, certificates and systemd timers for you.

`ngm2 install` installs required default nginx config (should call first)

`ngm2 html your.domain.com` instructs nginx to server static HTML files for given URL.

`ngm2 proxy your.domain.com/service1 8091` proxy given url to localhost:8091

`ngm2 add-auth <username> <password> <filename>` create basic-auth file that can be re-used for any nginx endpoint (html, webdav, proxy...). If an url wants to use the authentication, it needs to say `--use-auth filename` flag during creation. The `<filename>` can be simply an url that is intended to be protected for better memorizing it.

`ngm2 webdav your.domain.com/dav --use-auth <filename>` assigns a webdav endpoint to given URL and chooses a basic-auth protection for it defined in the previous step. Beware that you need to have `nginx-full` (which is the default nginx installation in Ubuntu) that supports third-party extension called webdav-ext.