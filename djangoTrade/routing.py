from channels.routing import route
from tradeBOT.consumers import ws_add, ws_disconnect

channel_routing = [
    route("websocket.connect", ws_add, path=r'^/trade/'),
    route("websocket.disconnect", ws_disconnect),
]
