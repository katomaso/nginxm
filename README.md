# ngm2

Tool to manage your nginx configuration. But not only! That would be too simple. It creates HTTPS certificates for your domains as well! Using letsencrypt. That would be still too simple. It even creates systemd timers to keep those certificates up-to-date.

Install by `pip install ngm2`. Now you have `ngm2` binary available.

## Usage

`ngm2 init` installs default nginx config required  by ngm2 for its functioning

`ngm2 html your.domain.com/` instructs nginx to server static HTML files for given URL.

`ngm2 proxy your.domain.com/service1 8091` proxy given url to localhost:8091

`ngm2 webdav your.domain.com/dav --use-auth <filename>` assigns a webdav endpoint to given URL and chooses a basic-auth protection for it defined with `add-auth` command. Beware that you need to have `nginx-full` (which is the default nginx installation in Ubuntu) that supports third-party extension called webdav-ext.

`ngm2 add-auth <filename> <username> <password>` create basic-auth file that can be re-used for any nginx endpoint (html, webdav, proxy...). If an url wants to use the authentication, it needs to say `--use-auth <filename>` flag during creation. The `<filename>` can have form of an url that is intended to be protected for better memorizing it.
