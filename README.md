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
apt-get install redis-server
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



**OpenEdx setup**
