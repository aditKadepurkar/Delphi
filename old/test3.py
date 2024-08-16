from openai import OpenAI
from dotenv import load_dotenv
import os

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
    load_dotenv()
    os.getenv("OPENAI_API_KEY")
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    
    function_code = response.choices[0].message.content
    function_code = function_code.replace("```", "")
    function_code = function_code.replace("python", "")
    print(function_code)
    exec(function_code, globals())
    
    
name = input("Give a function name(beware creating dangerous functions): ")
desc = input("Give a function description: ")
create_function(name, desc)
try:
    modify_file("old/random.txt", "the file should now be able trains instead of windows")
except NameError:
    print("Function not created")
