# entry point for the websocket loop
import gevent.monkey as gevent
import redis.connection


redis.connection.socket = gevent.socket
from ws4redis.uwsgi_runserver import uWSGIWebsocketServer
application = uWSGIWebsocketServer()
