from GPT_function_calling import OpenAI
from dotenv import load_dotenv
import time
from database import Database
from helpers import list_files
from GPT_function_calling import gpt_function_caller
from tools import Tools
from xLAM_function_calling import xlam_function_calling
import os

database = Database('doccollection')
print("Databse created")
database.add_to_database(file_list=list_files('test', ['txt', 'c', 'py']))
print("Database filled")

# load the model
tools = Tools()
res = input("xLAM or GPT?: ")
if res == "xLAM":
    client = xlam_function_calling()
if res == "GPT":
    client = gpt_function_caller()

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
        
    ]
    
    
    i = 0
    while True or i < 10:

        # print("Iteration", i)
        # print("Messages:", messages)


        available_functions = tools.get_available_functions()
        if res == "GPT":
            response = client.function_calling(messages=messages, tools=tools.get_tools(), available_functions=available_functions)
        if res == "xLAM":
            response = client.function_calling(messages=messages, query=query, tools=tools.get_tools(), available_functions=available_functions)
        if response == "Failed":
            break
        i += 1
        messages = response

    stop_time = time.time()
    
    print("Took", i, "iterations")
    print("Time taken:", stop_time - start_time)
