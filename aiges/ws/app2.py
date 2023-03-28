#!/usr/bin/env python
# coding:utf-8

import datetime
import os
import threading
import time
import json
import base64
import hashlib
import websocket
import gradio as gr

default_addr = "ws://localhost:1888/backup.0/private/chatgpt"
    class WebsocketWrapper(threading.Thread):
    def __init__(self, url):
        super(WebsocketWrapper, self).__init__()
        self.daemon = True
        self.ws = websocket.WebSocketApp(url, on_open=on_open)

    def run(self) -> None:
        self.ws.run_forever()
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

def on_open(ws):
    ws.send(construct_req(1))
def create_connection(key, addr, status):
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
    ws.ws.send(construct_req(1))
    # ws.connect(request_url)
    status = None

    return history, history, gr.Button.update("立即连接", interactive=False), gr.Button.update("取消", interactive=True)


count = 0
def construct_req(status=1):
    global count
    request_data_str = open("sample.json", 'rb').read()
    r = json.loads(request_data_str)
    r['header']['status'] = status
    global count, max_count
    count += 1
    print(count)
    if count >= 30:
        r['header']['status'] = 2
        r['payload']['message']['status'] = 2
    return json.dumps(r)


def cancel_connection():
    # todo cancel connection
    return gr.Button.update("立即连接", interactive=True), gr.Button.update("取消", interactive=False)


def chat(inp, history, agent):
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
        agent_state = gr.State()
        cnt_state = gr.State(False)
        submit.click(chat, inputs=[message, state, agent_state], outputs=[chatbot, state])
        message.submit(chat, inputs=[message, state, agent_state], outputs=[chatbot, state])
        cnt.click(create_connection, inputs=[openai_api_key_textbox, addr, cnt_state],
                  outputs=[chatbot, state, cnt, cancel])
        cancel.click(cancel_connection, None, outputs=[cnt, cancel])

    block.launch(debug=True)


if __name__ == '__main__':
    app()
