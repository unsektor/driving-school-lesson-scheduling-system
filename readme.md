## Installation

```bash
pip install -r requirements.txt
```

## OS X
### Installation

```bash
brew install nginx uwsgi
```

### Configuration
#### nginx

```
upstream uwsgi_app {
    server unix:/usr/local/run/uwsgi/app.sock;
}

server {
    listen       8100;
    server_name  localhost;

    location / {
        root   ".../src/public";
        index  index.html;
    }

    location /api/ {
        try_files $uri @uwsgi;
    }

    location @uwsgi {
        include uwsgi_params;
        uwsgi_pass uwsgi_app;
    }
}
```
 
 
#### uWSGI

```ini
[uwsgi]
socket = /usr/local/run/uwsgi/app.sock
chdir = .../src/sbin
pythonpath = .../src/lib
master = true
plugins = python3
file = api.py
callable = app
manage-script-name = true
```

### Start

```bash
uwsgi --ini /usr/local/etc/uwsgi/app.ini
nginx
```
