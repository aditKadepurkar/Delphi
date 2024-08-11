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

from database import Database
from helpers import list_files
from GPT_function_calling import gpt_function_caller
from tools import Tools




# embedmodel = getModel()
# modelfile = '''FROM llama3
# SYSTEM You have to give a clear and detailed and accurate description of the file contents and NOTHING else.
# ''' # I know it looks bad that the line above is not indented but it breaks the model if it is.
# ollama.create(model='example', modelfile=modelfile)


database = Database()
print("Databse created")
database.add_to_database(file_list=list_files('test', ['txt', 'c', 'py']))
print("Database filled")

# load the model
load_dotenv()
os.getenv("OPENAI_API_KEY")
client = OpenAI()

tools = Tools()

task_instruction = """
You are an expert in composing functions. You are given a question and a set of possible functions. 
Based on the question, you will need to make one or more function/tool calls to achieve the purpose. 
""".strip()

print("Starting the pipeline")

while True:
    
    query = input("Give a query: ") #"create a file in my test directory with a poem about summer"
    
    start_time = time.time()
    
    if query == "exit":
        print("Exiting the pipeline")
        break
    
    prompt = f"[BEGIN OF TASK INSTRUCTION]\n{task_instruction}\n[END OF TASK INSTRUCTION]\n\n"
    prompt += f"[BEGIN OF QUERY]\n{query}\n[END OF QUERY]\n\n"
    
    messages=[
        { 'role': 'user', 'content': prompt}
    ]
    
    
    i = 0
    while True or i < 10:  

        # print("Iteration", i)
        # print("Messages:", messages)

        gpt = gpt_function_caller(tools.get_tools())

        available_functions = tools.get_available_functions()

        response = gpt.call_func(messages=messages, tools=tools.get_tools(), available_functions=available_functions)
        if response == "Failed":
            break
        i += 1
        messages = response

    stop_time = time.time()
    
    print("Took", i, "iterations")
    print("Time taken:", stop_time - start_time)
