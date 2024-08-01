# Imports
import torch
import numpy as np
import chromadb
from chromadb import Collection
from sentence_transformers import (
    SentenceTransformer, models, losses, util, InputExample, evaluation, SentenceTransformerTrainingArguments, SentenceTransformerTrainer)
from accelerate import Accelerator
import glob
import os
from transformers import AutoModelForCausalLM, AutoTokenizer
import ollama
import json
import pygetwindow as gw
from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
from AppKit import NSWorkspace, NSApplication, NSRunningApplication
from Quartz.CoreGraphics import CGRectMake
import subprocess



def function_call(model, query, tools, format_instruction):
    """Calls one iteration of the function calling process."""
    
    task_instruction = """
    You are an expert in composing functions. You are given a question and a set of possible functions. 
    Based on the question, you will need to make one or more function/tool calls to achieve the purpose. 
    If none of the functions can be used, point it out and refuse to answer. 
    If the given question lacks the parameters required by the function, also point it out.
    """.strip()
    
    
    prompt = f"[BEGIN OF TASK INSTRUCTION]\n{task_instruction}\n[END OF TASK INSTRUCTION]\n\n"
    prompt += f"[BEGIN OF AVAILABLE TOOLS]\n{json.dumps(tools)}\n[END OF AVAILABLE TOOLS]\n\n"
    prompt += f"[BEGIN OF FORMAT INSTRUCTION]\n{format_instruction}\n[END OF FORMAT INSTRUCTION]\n\n"
    prompt += f"[BEGIN OF QUERY]\n{query}\n[END OF QUERY]\n\n"
    
    messages=[
        { 'role': 'user', 'content': prompt}
    ]
    
    
    # model.generation_config.pad_token_id = tokenizer.pad_token_id
    
    inputs = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt").to(model.device)
    outputs = model.generate(inputs, max_new_tokens=512, do_sample=False, num_return_sequences=1, eos_token_id=tokenizer.eos_token_id,  pad_token_id=tokenizer.eos_token_id)
    print(tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True))
    
def convert_to_xlam_tool(tools):
    ''''''
    if isinstance(tools, dict):
        return {
            "name": tools["name"],
            "description": tools["description"],
            "parameters": {k: v for k, v in tools["parameters"].get("properties", {}).items()}
        }
    elif isinstance(tools, list):
        return [convert_to_xlam_tool(tool) for tool in tools]
    else:
        return tools

def get_tools():
    """Get the available tools for the user to choose from.
    
    Format:
    [
        {
            "name": "func_name1",
            "description": "Description of the function",
            "parameters": {
                "argument1": "value1",
                "argument2": "value2"
            }
        },
    ]
    
    
    """
    
    return convert_to_xlam_tool(
        [
            {
                "name": "full_resize",
                "description": "Resize a window to the specified dimensions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "window_name": {
                            "type": "string",
                            "description": "The name of the window to resize"
                        },
                        "x": {
                            "type": "number",
                            "description": "The x-coordinate of the window"
                        },
                        "y": {
                            "type": "number",
                            "description": "The y-coordinate of the window"
                        },
                        "w": {
                            "type": "number",
                            "description": "The width of the window"
                        },
                        "h": {
                            "type": "number",
                            "description": "The height of the window"
                        }
                    },
                    "required": ["window_name", "x", "y", "w", "h"]
                }
            }
        ]
    )

def find_window(app_name):
    windows = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)
    for window in windows:
        # print(window)
        # if 'kCGWindowName' in window and 'kCGWindowOwnerName' in window:
            # print(window['kCGWindowOwnerName'])
        if window['kCGWindowOwnerName'] == app_name:
            return window
    return None

# Resize the window
def resize_window(window, x_bound, y_bound, width, height):
    # Get the window ID and current bounds
    # window_id = window['kCGWindowNumber']
    # bounds = window['kCGWindowBounds']
    
    # New position and size
    new_position = (x_bound, y_bound)
    new_size = (width, height)
    
    # Use an AppleScript command to resize the window
    script = f"""
    tell application "System Events"
        set the position of window 1 of process "{window["kCGWindowOwnerName"]}" to {{{new_position[0]}, {new_position[1]}}}
        set the size of window 1 of process "Discord" to {{{new_size[0]}, {new_size[1]}}}
    end tell
    """
    try:
        subprocess.run(['osascript', '-e', script])
        return "Success"
    except Exception as e:
        return e

def full_resize(window_name, x=0, y=0, w=1000, h=1000):
    window = find_window(window_name)
    if window:
        return resize_window(window, x, y, w, h)
    else:
        return (f"No window found for application {window_name}")

if __name__ == "__main__":
    # Set the seed for reproducibility
    torch.random.manual_seed(0)
    
    # load the model
    model_name = "Salesforce/xLAM-1b-fc-r"
    model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto", torch_dtype="auto", trust_remote_code=True)
    tokenizer = AutoTokenizer.from_pretrained(model_name) 

    # Instructions
    format_instruction = """
    The output MUST strictly adhere to the following JSON format, and NO other text MUST be included.
    The example format is as follows. Please make sure the parameter type is correct. If no function call is needed, please make tool_calls an empty list '[]'.
    ```
    {
        "tool_calls": [
        {"name": "func_name1", "arguments": {"argument1": "value1", "argument2": "value2"}},
        ... (more tool calls as required)
        ]
    }
    ```
    """.strip()
    
    
    

    query = "open up my new years resolutions"
    tools = get_tools()

    function_call(model=model, query=query, tools=tools, format_instruction=format_instruction)