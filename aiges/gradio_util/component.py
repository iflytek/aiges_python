#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: component.py
@time: 2023/01/11
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

import gradio as gr
from aiges.schema.types import *


def infer(image):
    result = image
    return result


class AISchemaGradioMapper(object):
    def __init__(self, _schema):
        self._schema = _schema
        self.inputbodymap = {
            "image": gr.Image,
            "audio": gr.Audio,
            "text": gr.Text,
        }

    def new_ui_by_schema(self, input_schema_json, output_schema_json):
        params = input_schema_json['definitions']['Paramodel']
        for p, d in params['properties'].items():
            if "type" not in d:
                continue
            if d['type'] == "string":
                text = gr.Text(label=p, type='text', visible=True, show_label=True)
                self.gr_inputs.append(text)
            elif d['type'] == "integer":
                pnum = gr.Number(label=p, visible=True, show_label=True)
                self.gr_inputs.append(pnum)
            elif d['type'] == "boolean":
                it = gr.Checkbox(label=p, visible=True, show_label=True)
                self.gr_inputs.append(it)
        pass

    def new_gradio_component(self, m: BaseModel, key: str):
        print(type(m))
        print(dir(m))

        if isinstance(m, ImageField):
            image = gr.Image(label=key, type='filepath', visible=True, show_label=True)
            self.gr_inputs.append(image)
        elif isinstance(m, TextField):
            text = gr.Text(label=key, type='text', visible=True, show_label=True)
            self.gr_inputs.append(text)

        elif isinstance(m, AudioField):
            audio = gr.Audio(label=key, type='numpy', visible=True, show_label=True)
            self.gr_inputs.append(audio)
        elif isinstance(m, str):
            pstr = gr.Textbox(label=key, type='text', visible=True, show_label=True)
            self.gr_inputs.append(pstr)
        elif isinstance(m, bool):
            pbool = gr.Checkbox(label=key, visible=True, show_label=True)
            self.gr_inputs.append(pbool)

        elif isinstance(m, int) | isinstance(m, float):
            pnum = gr.Number(label=key, visible=True, show_label=True)
            self.gr_inputs.append(pnum)

    def run(self):
        with gr.Blocks() as self.gr_demo:
            title = gr.Markdown("""
            # Gradio Demo ASF aiges demo
            """)
            self.gr_inputs = []
            self.gr_outputs = []
            title = gr.Markdown("""
               ## demo's input params(控制字段)
               """)
            with gr.Row(equal_height=True):
                # self._schema.schemainput.schema()['definitions']['Paramodel'] todo
                a = self._schema.schemainput.schema_json()
                self.new_ui_by_schema(self._schema.schemainput.schema(), self._schema.schemaoutput.schema())
        #                    for p in self._schema.schemainput.parameter.__fields__:
        #                        self.new_gradio_component(self._schema.schemainput.parameter.__dict__.get(p), p)

            title = gr.Markdown("""
            ## demo's input body(body输入)
            """)
            with gr.Row(equal_height=True):
                for f in self._schema.schemainput.payload.__fields__:
                    self.new_gradio_component(self._schema.schemainput.payload.__dict__.get(f), f)

            title = gr.Markdown("""
            ## demo's outputs (推理输出)
            """)
            with gr.Row(equal_height=True):
                for p in self._schema.schemaoutput.payload.__fields__:
                    self.new_gradio_component(self._schema.schemaoutput.payload.__dict__.get(p), p)

            run_button = gr.Button('Run')
            run_button.click(fn=infer, inputs=self.gr_inputs, outputs=self.gr_outputs)

        self.gr_demo.launch(share=False, server_name='0.0.0.0', server_port=7861)


class GradioComponent(object):
    def __init__(self, ai_schema):
        self._schema = ai_schema
        inputs = []
        self.ui = AISchemaGradioMapper(ai_schema)

    def prepareUI(self):
        pass

    def schemaToGradio(self):
        pass

    def run(self):
        self.ui.run()
