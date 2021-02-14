# nginxm

Simple management tool for nginx's virtual servers with automatic SSL certificates.
It uses systemd timers for renewals of the certificates.

## Configuration

Install by `pip install nginxm`. Now you have `ngm` entry point available. 

Ngm supposes that only HTTP traffic is handled by your current nginx's config
```
server {
	listen 80 default_server;
	listen [::]:80 default_server;

	server_name _;

	location /.well-known/acme-challenge/ {
		root /var/www/;
	}

	location / {
		return 301 https://$host$request_uri;
	}
}
```
