import os
import subprocess
from helpers import find_window, resize_window
from openai import OpenAI
from database import add_to_database

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

def create_function(function_name: str, function_description: str):
    '''
    Create and run a function using a function name an description that is passed
    to GPT-4o-mini to create a function that will be called.
    
    @param query: str: The query to be processed.
    @return: str: The function to be called.
    '''
    
    messages=[
        {'role': 'system', 'content': 'You have to create a function based on the given description. NO OTHER TEXT.'},    
        {'role': 'user', 'content': f"Create a function called {function_name} that does {function_description}"}
    ]
    client = OpenAI()
    client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    
    function_code = response.choices[0].message.content
    exec(function_code)