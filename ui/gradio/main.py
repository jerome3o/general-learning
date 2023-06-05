import gradio as gr


def greet(name: str):
    return "Hello " + name + "!"


demo = gr.Interface(fn=greet, inputs="text", outputs="text")
demo.launch()
