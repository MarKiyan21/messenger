from channels.routing import route
from messenger.consumer import priv_connect, priv_receive, priv_disconnect

channel_routing = [
    route("websocket.connect", priv_connect, path=r"^/private"),
    route("websocket.receive", priv_receive, path=r"^/private"),
    route("websocket.disconnect", priv_disconnect, path=r"^/private"),
]