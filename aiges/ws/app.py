#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: app.py
@time: 2023/03/10
@contact: ybyang7@iflytek.com
@site:  
@software: PyCharm 

# code is far away from bugs with the god animal protecting
    I love animals. They taste delicious.
              ┏┓      ┏┓
            ┏┛┻━━━┛┻┓
            ┃      ☃      ┃
            ┃  ┳┛  ┗┳  ┃
            ┃      ┻      ┃
            ┗━┓      ┏━┛
                ┃      ┗━━━┓
                ┃  神兽保佑    ┣┓
                ┃　永无BUG！   ┏┛
                ┗┓┓┏━┳┓┏┛
                  ┃┫┫  ┃┫┫
                  ┗┻┛  ┗┻┛ 
"""

#  Copyright (c) 2022. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

import datetime
import os
import queue
import threading
import time
import json
import base64
import hashlib
import websocket
import gradio as gr

default_addr = "ws://localhost:1888/backup.0/private/chatgpt"

ws = None

result_queue = queue.Queue(1)

class WebsocketWrapper(threading.Thread):
    def __init__(self, url):
        super(WebsocketWrapper, self).__init__()
        self.daemon = False
        self.url = url
        self.status = False

    def run(self) -> None:
        self.ws = websocket.WebSocketApp(self.url, on_open=on_open, on_message=on_message, on_close=on_close)

        a = self.ws.run_forever()
        print("Done")

    def keep_alive(self):
        pass


def connect(api_key, add=default_addr):
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        # vectorstore = get_weaviate_store()
        # qa_chain = get_new_chain1(vectorstore)
        os.environ["OPENAI_API_KEY"] = ""
        # return qa_chain


def check_and_connect(key, addr):
    # todo
    if not addr:
        # check url todo
        return "please specify websocket url... ", -1

    return "connected %s" % addr, None


def readb64(index, encoded_data):
    # img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # return img
    b = base64.b64decode(encoded_data)
    print(hashlib.md5(b).hexdigest())
    print(len(b))
    # a = open(str(index) + ".jpg", "wb")
    # a.write(b)
    # a.close()
    return b.decode("utf-8")


def on_close(ws, code, reason):
    print("closed!!!", code, reason)


def on_open(ws):
    global count
    count = 0
    print(1)
    ws.send(construct_req(1))


# 收到websocket消息的处理
def on_message(ws, message):
    if message == "":
        return
    temp_result = json.loads(message)
    print(temp_result)
    global result_queue
    # print("响应数据:{}\n".format(temp_result))
    header = temp_result.get('header')
    if header is None:
        return 2, "失败"
    code = header.get('code')
    if header is None or code != 0:
        print("获取结果失败，请根据code查证问题原因:, %s" % code)
        return 2, "失败"
    text = ''
    if "payload" in temp_result:
        i = temp_result['payload']['response']['text']
        index = temp_result['payload']['response']['seq']
        text = readb64(index, i)
        print(text)
        result_queue.put(text)


    # print("sid:{}".format(header.get('sid')))
    status = header.get('status')
    # if status == 1:
    #     print("dddcccc")
    #     ws.send(construct_req(1))

    # print('status:{}\n'.format(status))
    return int(status), text


def create_connection(key, addr, status):
    global ws
    history = []
    init_msg = "connecting ws..."
    print(init_msg)

    # todo call ws create functions
    #
    msg, err = check_and_connect(key, addr)
    output = {"question": init_msg, "chat_history": history, "answer": msg}

    answer = output["answer"]
    history.append((init_msg, answer))
    status = not status

    # create ws
    # request_data_str = json.load(a)
    # auth_request_url = build_auth_request_url(request_url, "GET", APIKey, APISecret)
    ws = WebsocketWrapper(addr)
    ws.start()
    # ws.connect(request_url)
    status = None

    return history, history, gr.Button.update("立即连接", interactive=False), gr.Button.update("取消", interactive=True)


count = 0


def construct_req(status=1, message=""):
    global count
    request_data_str = open("sample.json", 'rb').read()
    r = json.loads(request_data_str)
    r['header']['status'] = status
    global count, max_count
    # count += 1
    # print(count)
    # if count >= 30:
    r['header']['status'] = 1
    r['payload']['message']['status'] = 1
    r['payload']['message']['text'] = base64.b64encode(message.encode("utf-8")).decode('utf-8')
    return json.dumps(r)


def cancel_connection():
    # todo cancel connection
    return gr.Button.update("立即连接", interactive=True), gr.Button.update("取消", interactive=False)


def chat2(inp, history, agent):
    history = history or []
    if agent is None:
        history.append((inp, "Please paste your OpenAI key to use"))
        return history, history
    print("\n==== date/time: " + str(datetime.datetime.now()) + " ====")
    print("inp: " + inp)
    history = history or []
    output = agent({"question": inp, "chat_history": history})
    answer = output["answer"]
    history.append((inp, answer))
    print(history)
    return history, history


def chat(inp, history):
    global ws
    print(inp)
    ws.ws.send(construct_req(1, inp))
    history = history or []
    result = result_queue.get()
    history.append((inp, result))
    return history, history


def app():
    block = gr.Blocks(css=".gradio-container {background-color: lightgray}")

    with block:
        with gr.Row():
            gr.Markdown("<h3><center>AILab Demo Bot AI</center></h3>")
            with gr.Column():
                openai_api_key_textbox = gr.Textbox(
                    placeholder="Paste your OpenAI API key (sk-...)",
                    show_label=False,
                    lines=1,
                    type="password",
                )
                addr = gr.Textbox(
                    default_addr,
                    placeholder="Paste your Service URL",
                    show_label=False,

                    lines=1, type="text", elem_id="addr"
                )
            with gr.Column():
                cnt = gr.Button(value="立即连接", variant="primary", elem_id="cnt")
                cancel = gr.Button(value="取消", elem_id="cancel", interactive=False)

        chatbot = gr.Chatbot()
        with gr.Column():
            with gr.Row():
                message = gr.Textbox(
                    label="What's your question?",
                    placeholder="What's the answer to life, the universe, and everything?",
                    lines=1,
                )
                submit = gr.Button(value="Send", variant="secondary").style(full_width=False)

        gr.Examples(
            examples=[
                "What are agents?",
                "How do I summarize a long document?",
                "What types of memory exist?",
            ],
            inputs=message,
        )

        gr.HTML(
            """
        This simple application is an implementation of ChatGPT but over an external dataset (in this case, the LangChain documentation)."""
        )

        gr.HTML(
            "<center>Powered by <a href='https://github.com/iflytek/ailab'>AILab 🦜️🔗</a></center>"
        )
        state = gr.State()

        cnt_state = gr.State(False)
        submit.click(chat, inputs=[message, state], outputs=[chatbot, state])
        #message.submit(chat, inputs=[message, state], outputs=[chatbot, state])
        cnt.click(create_connection, inputs=[openai_api_key_textbox, addr, cnt_state],
                  outputs=[chatbot, state, cnt, cancel])
        cancel.click(cancel_connection, None, outputs=[cnt, cancel])

    block.launch(debug=True,server_name="0.0.0.0")


if __name__ == '__main__':
    app()
