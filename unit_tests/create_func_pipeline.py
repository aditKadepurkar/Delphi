import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from default_tools import create_function
from dotenv import load_dotenv
import time
from database import Database
from helpers import list_files
from GPT_function_calling import gpt_function_caller
from tools import Tools
from xLAM_function_calling import xlam_function_calling
from openai import OpenAI
import json

create_func_tool = {"create_function": create_function}


create_func_tool_json = [{
    "type": "function",
    "function": {
        "name": "create_function",
        "description": "Creates a function with the given name and description",
        "parameters": {
            "type": "object",
            "properties": {
                "function_name": {
                    "type": "string",
                    "description": "The name of the function"
                },
                "function_description": {
                    "type": "string",
                    "description": "The description of the function"
                }
            },
            "required": ["name", "description"]
        }
    }
}]


# We are simulating having gpt create the function from our task.
query = input("Give a query: ")

# openai setup
load_dotenv()
os.getenv("OPENAI_API_KEY")
client = OpenAI()

# messages
task_instruction = """
You are an expert in composing functions. You are given a question and a set of possible functions. 
Based on the question, you will need to make one or more function/tool calls to achieve the purpose. 
""".strip()

prompt = f"[BEGIN OF TASK INSTRUCTION]\n{task_instruction}\n[END OF TASK INSTRUCTION]\n\n"
prompt += f"[BEGIN OF QUERY]\n{query}\nOS: MACOS\n[END OF QUERY]\n\n"

messages=[
    { 'role': 'user', 'content': prompt}
]

response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=create_func_tool_json,
        tool_choice="auto"
    )


response_message = response.choices[0].message
tool_calls = response_message.tool_calls

if tool_calls:
    messages.append(response_message)
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function = create_func_tool[function_name]
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

print(func_response)

# create the function
# exec(func_response, globals())

with open('unit_tests/test_create_func.py', 'a') as f:
    f.write(func_response + '\n')
    # f.write('\n\n')
