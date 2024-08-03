"""This file has a pipeline using OpenAI's API to perform a task of calling functions based on a query.
It currently takes an input query and outputs a set of function calls to achieve the desired task.
Will work on vocal input and output in the future.

Built by Adit Kadepurkar on 08/01/24
"""


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
# import transformers
# from transformers import AutoModelForCausalLM, AutoTokenizer
import ollama
import json
import pygetwindow as gw
from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
from AppKit import NSWorkspace, NSApplication, NSRunningApplication
from Quartz.CoreGraphics import CGRectMake
import subprocess
from openai import OpenAI
from dotenv import load_dotenv
import uuid
import time


# Helper functions
# These functions are used by the main function to perform the required tasks.
# 
def get_function_to_call(client, messages, tools, available_functions):
    """Calls one iteration of the function calling process."""
    
    
    # Get the response
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    
    
    
    if tool_calls:
        messages.append(response_message)
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function = available_functions[function_name]
            parameters = json.loads(tool_call.function.arguments)
            
            func_response = function(
                **parameters
            )
            
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": func_response,
                }
            )
        return messages
    return "Failed"
    
def get_available_functions():
    """Get the available functions for the user to choose from.
    Format:
    {
        "func_name1": func1,
        "func_name2": func2
    }
    """
    available_functions = {
        "full_resize": full_resize,
        "create_file": create_file,
        "remove_file": remove_file,
        "search_files": search_files,
        "open_file": open_file,
        "generate_text": generate_text,
        "list_files": list_files,
        "list_directories": list_directories,
        "open_application": open_application,
        "close_application": close_application,
        "list_applications": list_applications,
    }
    return available_functions

def get_tools():
    """Get the available tools for the user to choose from."""
    
    # so far:
    # 1. full_resize, 2. list_directories, 3. create_file, 4. generate_text, 5. open_file, 6. search_files, open_application
    tools = [
        {
            "type": "function",
            "function": {
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
        },
        {
            "type": "function",
            "function": {
                "name": "list_directories",
                "description": "List all the directories in the current directory.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_file",
                "description": "Create a file at the given file path with the given content.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The path of the file to be created. Defaults to Delphi directory."
                        },
                        "content": {
                            "type": "string",
                            "description": "The content of the file."
                        }
                    },
                    "required": ["file_path", "content"],
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "generate_text",
                "description": "Generates text given a prompt",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "The prompt to generate text based on."
                        },
                    },
                    "required": ["prompt"],
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "open_file",
                "description": "Open the file at the given file path if it is VALID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The path of the file to be opened."
                        },
                    },
                    "required": ["file_path"],
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_files",
                "description": "Search for the file that matches query and return the file path.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The query to search for the file. This query should be something that is semantically similar to what we are looking for.",
                        },
                        "collection": {
                            "type": "string",
                            "description": "The collection to search in. (Use doccollection for now)"
                        },
                        "embedmodel": {
                            "type": "string",
                            "description": "The model to be used for getting the embeddings. (Use embedmodel for now)"
                        }
                    },
                    "required": ["query"],
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "open_application",
                "description": "Open the application with the given name. Make sure you use the correct application name for mac.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "app_name": {
                            "type": "string",
                            "description": "The name of the application to be opened."
                        },
                    },
                    "required": ["app_name"],
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_applications",
                "description": "List all the applications that are currently running.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "close_application",
                "description": "Close the application with the given name.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "app_name": {
                            "type": "string",
                            "description": "The name of the application to be closed."
                        },
                    },
                    "required": ["app_name"],
                }
            }
        }
    ]
    return tools

def getEmbeddingList(model, sentences):
  """ This function returns the sentence embeddings for a given document using the SentenceTransformer model and encapsulates them inside a list.

  @param model: SentenceTransformer: The model to be used for getting the embeddings.
  @param sentences: list: The list of sentences for which embeddings are to be calculated. """

  embeddings = model.encode(sentences)
  return embeddings.tolist()

def getModel() -> SentenceTransformer:
  """ This function creates a SentenceTransformer model using the 'sentence-transformers/all-MiniLM-L6-v2' base model. It utilizes accelerator to make use of multiple GPUs
  and adds a layer to get the sentence embeddings via mean pooling. This model will be used for training sbert's sentence embeddings. """

  accelerator = Accelerator()
  print(f"Using GPUs: {accelerator.num_processes}")

  # Get the base model to train
  word_embedding_model = models.Transformer('sentence-transformers/all-MiniLM-L6-v2')

  # Add layer to get "sentence embedding" (using mean pooling)
  pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
  model = SentenceTransformer(modules=[word_embedding_model, pooling_model])
  return model

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
    
def get_ollama_description(file_path: str, modelfile: str):
    """
    Get the description of the input from the Ollama model.
    
    @param file_path: str: The file with the document.
    @param modelfile: str: The modelfile for the Ollama model.
    @return: str: The description of the input.
    """
    content = get_document_info(file_path)
    # print(content)
    ollama.create(model='example', modelfile=modelfile)
    response = ollama.chat(model="example", messages=[
        {
            'role': 'user',
            'content': f'Filename: {os.path.basename(content[0])}, File content:{content[1]}'
        }])
    return response['message']['content']    

def add_to_database(file_list: list):

    sentences = []
    ids = []
    for file in file_list:
        sentences.append(get_ollama_description(file_path=file, modelfile=modelfile)) # need to start saving these so it doesnt take 100 years for the program to run each time
        ids.append(str(uuid.uuid4())) # generate a random id for each file
    # print(sentences)
    embeds = getEmbeddingList(model=embedmodel, sentences=sentences)
    doc_collection.add(
        embeddings=embeds,
        documents=file_list,
        ids=ids,
    )




# Helper functions more specific to tool calls
# These will be called by the tools to perform the required tasks.
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


# Tools
# These functions are the tools that will be called to perform the required tasks.
# These functions are passed to OpenAI's API to be called based on the query.

def full_resize(window_name, x=0, y=0, w=1000, h=1000):
    window = find_window(window_name)
    if window:
        return resize_window(window, x, y, w, h)
    else:
        return (f"No window found for application {window_name}")
    
def create_file(file_path: str, content: str):
    '''
    Create a file at the given file path with the given content.
    
    @param file_path: str: The path of the file to be created.
    @param content: str: The content of the file.
    '''
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        add_to_database(file_list=[file_path])
        return "Success"
    except:
        return "Failed"

def remove_file(file_path: str):
    '''
    Remove the file at the given file path.
    
    @param file_path: str: The path of the file to be removed.
    '''
    os.remove(file_path)
    
    return "Success"
    
def search_files(query: str):
    '''
    Search for files in the collection that match the query.
    
    @param query: str: The query to search for.
    @param collection: Collection: The collection to search in.
    @param embedmodel: SentenceTransformer: The model to be used for getting the embeddings.
    @return: list: The list of files that match the query.
    '''
    query_result = doc_collection.query(
        query_embeddings=[getEmbeddingList(embedmodel, query)],
        n_results=1,
    )
    return query_result['documents'][0][0]

def open_file(file_path: str):
    '''
    Open the file at the given file path.
    
    @param file_path: str: The path of the file to be opened.
    '''
    try:
        if os.path.exists(file_path):
            subprocess.run(['open', file_path])
            return "Success"
        else:
            return "File does not exist"
    except:
        return "Failed"

def generate_text(prompt):
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{'role': 'user', 'content': f"Write some text for the following prompt: {prompt} and NO OTHER TEXT OF ANY KIND YOU DO EXACTLY AS TOLD"}],
    )
    return res.choices[0].message.content

def list_directories():
    '''
    List all the directories in the current directory.
    
    @return: list: The list of directories in the current directory.
    '''
    return ', '.join([name + '/' for name in os.listdir() if os.path.isdir(name)])

def open_application(app_name: str):
    '''
    Open the application with the given name.
    
    @param application_name: str: The name of the application to be opened.
    '''
    try: 
        os.system(f'open -a {app_name}')
        return "Success"
    except:
        return "Failed"

def close_application(app_name: str):
    '''
    Close the application with the given name.
    
    @param application_name: str: The name of the application to be closed.
    '''
    try:
        os.system(f'killall {app_name}')
        return "Success"
    except:
        return "Failed"

def list_applications():
    '''
    List all the applications that are currently running.
    
    @return: list: The list of applications that are currently running.
    '''
    running_apps = [app.localizedName() for app in NSWorkspace.sharedWorkspace().runningApplications()]
    return ', '.join(running_apps)

# main function
if __name__ == "__main__":
    # Set the seed for reproducibility
    torch.random.manual_seed(0)
    
    # Build the database
    embedmodel = getModel()
    modelfile = modelfile = '''FROM llama3
SYSTEM You have to give a clear and detailed and accurate description of the file contents and NOTHING else.
    ''' # I know it looks bad that the line above is not indented but it breaks the model if it is.
    ollama.create(model='example', modelfile=modelfile)
    client = chromadb.Client()
    doc_collection = client.get_or_create_collection("docs")
    add_to_database(file_list=list_files('test', ['txt', 'c', 'py']))
    
    # load the model
    load_dotenv()
    os.getenv("OPENAI_API_KEY")
    client = OpenAI()
    
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

            tools = get_tools()
            available_functions = get_available_functions()

            response = get_function_to_call(client=client, messages=messages, tools=tools, available_functions=available_functions)
            if response == "Failed":
                break
            i += 1
            messages = response
        
        stop_time = time.time()
        
        print("Took", i, "iterations")
        print("Time taken:", stop_time - start_time)

