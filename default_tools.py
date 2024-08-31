import os
import subprocess
from helpers import find_window, resize_window, list_files
from GPT_function_calling import OpenAI
from dotenv import load_dotenv
from AppKit import NSWorkspace
from database import Database

database = Database('doccollection')

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
        database.add_to_database(file_list=[file_path])
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
    query_result = database.query_database(
        query=query,
    )
    return query_result

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
    load_dotenv()
    os.getenv("OPENAI_API_KEY")
    client = OpenAI()
    
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

def create_function(function_name: str, function_description: str):
    '''
    Create and run a function using a function name an description that is passed
    to GPT-4o-mini to create a function that will be called.
    
    @param query: str: The query to be processed.
    @return: str: The function to be called.
    '''
    
    messages=[
        {'role': 'system', 'content': 'You have to create a function based on the given description. NO OTHER TEXT. DO NOT create a codeblock, plaintext of ONLY the function'},    
        {'role': 'user', 'content': f"Create a function called {function_name} that does {function_description}"}
    ]

    load_dotenv()
    os.getenv("OPENAI_API_KEY")
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    
    function_code = response.choices[0].message.content

    # exec(function_code, globals())

    return function_code


DEFAULT_TOOLS = {
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
"""Default tools as function objects in a dictionary"""

DEFAULT_TOOLS_JSON = [
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
"""Default tools as JSON objects"""
