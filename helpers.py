import torch
import numpy as np
import chromadb
from chromadb import Collection
from sentence_transformers import (
    SentenceTransformer, models, losses, util, InputExample, evaluation, SentenceTransformerTrainingArguments, SentenceTransformerTrainer)
from accelerate import Accelerator
import glob
import os
# import transformers
# from transformers import AutoModelForCausalLM, AutoTokenizer
import ollama
import json
import pygetwindow as gw
from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
from AppKit import NSWorkspace, NSApplication, NSRunningApplication
from Quartz.CoreGraphics import CGRectMake
import subprocess
from GPT_function_calling import OpenAI
from dotenv import load_dotenv
import uuid
import time

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
        set the size of window 1 of process "{window["kCGWindowOwnerName"]}" to {{{new_size[0]}, {new_size[1]}}}
    end tell
    """
    try:
        subprocess.run(['osascript', '-e', script])
        return "Success"
    except Exception as e:
        return e

def list_files(initdir: str, file_extensions: list):
    '''
    Returns a list of file under initdir and all its subdirectories
    that have file extension contained in file_extensions.
    ''' 
    file_list = []
    file_count = {key: 0 for key in file_extensions}  # for reporting only
    
    # Traverse through directories to find files with specified extensions
    for root, _, files in os.walk(initdir):
        for file in files:
            ext = file.split('.')[-1].lower()
            if ext in file_extensions:
                file_path = os.path.join(root, file)
                file_list.append(file_path)
                # increment type of file
                file_count[ext] += 1
    
    # total = len(file_list)
    # print(f'There are {total} files under dir {initdir}.')
    # for k, n in file_count.items():
        # print(f'   {n} : ".{k}" files')
    return file_list

def getModel() -> SentenceTransformer:
    """ This function creates a SentenceTransformer model using the 'sentence-transformers/all-MiniLM-L6-v2' base model. It utilizes accelerator to make use of multiple GPUs
    and adds a layer to get the sentence embeddings via mean pooling. This model will be used for training sbert's sentence embeddings. """

    accelerator = Accelerator()
    print(f"Using GPUs: {accelerator.num_processes}")

  # Get the base model to train
#   word_embedding_model = models.Transformer('sentence-transformers/all-MiniLM-L6-v2')

  # Add layer to get "sentence embedding" (using mean pooling)
#   pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
#   model = SentenceTransformer(modules=[word_embedding_model, pooling_model])
    model = SentenceTransformer("multi-qa-mpnet-base-cos-v1")
    return model

def get_description(file_path: str):
    """
    Get the description of the input from the Ollama model.
    
    @param file_path: str: The file with the document.
    @param modelfile: str: The modelfile for the Ollama model.
    @return: str: The description of the input.
    """
    content = get_document_info(file_path)
    # print(content)
    
    load_dotenv()
    os.getenv("OPENAI_API_KEY")
    client = OpenAI()

    messages=[
        {"role": "system", "content": "You give clear descriptions of the file passed to you."},
        {'role': 'user', 'content': f'Filename: {os.path.basename(content[0])}, File content:{content[1]}'}
        ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    
    return response.choices[0].message.content

def convert_to_xlam_tools(tools):
    ''''''
    if isinstance(tools, dict):
        return {
            "name": tools["name"],
            "description": tools["description"],
            "parameters": {k: v for k, v in tools["parameters"].get("properties", {}).items()}
        }
    elif isinstance(tools, list):
        return [convert_to_xlam_tools(tool) for tool in tools]
    else:
        return tools

def get_document_info(file_path: str):
    '''
    Open the file at the given file path and return its content.
    
    @param file_path: str: The path of the file to be opened.
    @return: str: The content of the file.
    '''
    try: 
        with open(file_path, 'r') as file:
            content = file.read()
        # metadata = file.metadata
        file_name = file_path
        return (file_name, content)
    except:
        return None

def get_tool_json(function):
    name = function.__name__
    arg_count = function.__code__.co_argcount
    params = function.__code__.co_varnames
    
    dict = {}
    dict['name'] = name
    dict['description'] = ""
        
    
    
    ret_json = {}
    ret_json['type'] = "function"
    ret_json['function'] = dict
