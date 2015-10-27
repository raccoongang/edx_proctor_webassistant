# Instalation guide

**Proctor web assistant installation**

Create venv and activate it
```
virtualenv --no-site-packages edx_web_assistant_venv
source edx_web_assistant_venv/bin/activate
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
Setup the project
```
cd edx_proctor_webassistant
pip install -r requirements.txt 
```
Create file `local_settings.py` in one level with settings.py and specify BOWER_PATH there. For example:
```
BOWER_PATH = '/usr/local/bin/bower'
```
Also set `EDX_URL` in settings

Then run commands
```
python manage.py bower install
python manage.py syncdb
```
**SSO authorization setup**
- Create new client i SSO
- Enter client's KEY and SECRET in web assistant's settings:
```
    SOCIAL_AUTH_SSO_NPOED_OAUTH2_KEY = '<KEY>'
    SOCIAL_AUTH_SSO_NPOED_OAUTH2_SECRET = '<SECRET>'
```
- Enter SSO application's url in web assistant's settings:
```
    SSO_NPOED_URL = "http://<SSO url>"
```


