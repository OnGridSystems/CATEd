from channels import Group


def ws_add(message):
    message.reply_channel.send({"accept": True})
    Group("trade").add(message.reply_channel)


def ws_disconnect(message):
    Group("trade").discard(message.reply_channel)
