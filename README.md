# Instalation guide

## Proctor web assistant installation

Create venv and activate it
```
virtualenv --no-site-packages assistant_env
source assistant_env/bin/activate
```

Install bower using npm
```
npm install -g bower
```

Get source from GitHub
```
git clone https://github.com/raccoongang/edx_proctor_webassistant
```

Install few tools
```
sudo apt-get install redis-server
sudo apt-get install libffi-dev
pip install cython git+git://github.com/gevent/gevent.git#egg=gevent
```

Check redis server is running
```
redis-cli ping
>>> PONG
```

Setup the project
```
cd edx_proctor_webassistant
pip install -r requirements.txt 
```

Create file `settings_local.py` in one level with settings.py and specify BOWER_PATH there. For example:
```
BOWER_PATH = '/usr/local/bin/bower'
```

Also set `EDX_URL` in settings

If EDX use course_id pattern as 'foo:bar+fooo+bar' add 
`COURSE_ID_SLASH_SEPARATED = False` into your local_settings

Then run commands
```
python manage.py bower install
python manage.py migrate
python manage.py collectstatic
```

## SSO authorization setup

- Create new client in SSO admin panel. Set redirect uri as `http://<domain>/complete/sso_npoed-oauth2/`
- Enter client's KEY and SECRET in web assistant's settings:
```
    SOCIAL_AUTH_SSO_NPOED_OAUTH2_KEY = '<KEY>'
    SOCIAL_AUTH_SSO_NPOED_OAUTH2_SECRET = '<SECRET>'
```

- Enter SSO application's url in web assistant's settings:
```
    SSO_NPOED_URL = "http://<SSO url>"
```
- Set up an `AUTH_SESSION_COOKIE_DOMAIN`. It must be proctor domain address without subdomain. For example `.yourdomain.com` for `proctor.yourdomain.com`

- By default webassistant supports slash separated course id (for example `org/course/course_run`). If course id pattern looks like `course-v1:org+course+course_run` set `COURSE_ID_SLASH_SEPARATED = False` 


## Setup uWSGI

**NOTE:** if you run application locally and `DEBUG=True`, no uwsgi configuration is needed

Install uwsgi globally
```
sudo pip install uwsgi
```

All actions below will be considered from the point when your cloned code lives in `/edxapps`.

We will be using uwsgi in emperror mode. One process for django application and another one for websocket server.

Create somewhere the file named `uwsgi.ini` with the following content (assuming you want to run django server on `:8080` port)
```
[uwsgi]
emperor = vassals
uid = www-data
gid = www-data
die-on-term = true
offload-threads = 1
route = ^/ws uwsgi:/tmp/web.sock,0,0
route = ^/ uwsgi:/127.0.0.1:8080,0,0
```

Create `vassals` dir with 2 configs (change path to the directory where uwsgi.ini was created)
```
# mkdir /edxapp/edx_proctor_webassistant/vassals
# cd /edxapp/edx_proctor_webassistant/vassals
# touch runserver.ini
# touch websocket.ini
```

runserver.ini content for django application (change params to your according to your needs): 
```
[uwsgi]
umask = 002
userhome = /tmp
virtualenv = /edxapps/assistant_env
chdir = /edxapps/edx_proctor_webassistant
master = true
no-orphans = true
die-on-term = true
memory-report = true
env = DJANGO_SETTINGS_MODULE=edx_proctor_webassistant.settings
socket = 127.0.0.1:8080
module = edx_proctor_webassistant.wsgi
buffer-size = 32768
processes = 2
```

websocket.ini content for websocket server:
```
[uwsgi]
umask = 002
virtualenv = /edxapps/assistant_env
chdir = /edxapps/edx_proctor_webassistant
module = edx_proctor_webassistant.wsgi_socket
no-orphans = true
die-on-term = true
memory-report = true
http-socket = /tmp/web.sock
http-websockets = true
gevent = 1000
processes = 1
master = true
```

check the config is correct
```
# cd /edxapp/edx_proctor_webassistant
# uwsgi --ini uwsgi.ini
```

## NGINX

Upgrade your Nginx version to >=1.4
 
Nginx server allows us to serve our static files and supports websockets switching protocol feature
 
Create `proctor` config (or place a symlink) in nginx sites-available dir
```
upstream django {
    server 127.0.0.1:8080;
}

upstream websocket {
    server unix:/tmp/web.sock;
}

server {
    listen 80;
    server_name proctor.sandbox; # place your server name here

    charset utf-8;
    client_max_body_size 20M;
    keepalive_timeout 0;
    large_client_header_buffers 8 32k;

    access_log /var/log/nginx/proctoring_access.log;
    error_log /var/log/nginx/proctoring_error.log;

    location / {
        include /etc/nginx/uwsgi_params;
        uwsgi_pass django;
    }

    location /static {
        alias /edxapps/edx_proctor_webassistant/static;
    }

    location /ws/ {
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_pass http://unix:/tmp/web.sock;
        proxy_buffers 8 32k;
        proxy_buffer_size 64k;
   }
}
```
