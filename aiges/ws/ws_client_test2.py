
def on_error(wsapp, err):
print("EXAMPLE error encountered: ", err)


# 收到websocket消息的处理
def on_message(ws, message):
    if message == "":
        return
    temp_result = json.loads(message)
print(temp_result)