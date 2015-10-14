import json
from ws4redis.redis_store import RedisMessage
from ws4redis.publisher import RedisPublisher
from django.conf import settings


def send_ws_msg(data, channel=settings.WEBSOCKET_EXAM_CHANNEL):
    """
    Send message to websocket service through Redis
    """
    ws_msg = RedisMessage(json.dumps(data))
    RedisPublisher(
        facility=channel,
        broadcast=True
    ).publish_message(ws_msg)
