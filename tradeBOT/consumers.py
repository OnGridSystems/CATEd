# In consumers.py
from channels import Group


# Connected to websocket.connect
def ws_add(message):
    # Accept the connection
    message.reply_channel.send({"accept": True})
    # Add to the chat group
    Group("trade").add(message.reply_channel)


# Connected to websocket.disconnect
def ws_disconnect(message):
    Group("trade").discard(message.reply_channel)
