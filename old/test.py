

# def get_tool_json(function):
#     name = function.__name__
#     arg_count = function.__code__.co_argcount
#     params = function.__code__.co_varnames
#     desc = function.__doc__
    
#     print(name)
#     print(arg_count)
#     print(params)
#     print(desc)
    

# def real(input, bizz):
#     """
#     text that is the summary

#     @param param_1: type1: desc
#     @return: type2: desc
#     """
#     pass

# get_tool_json(real)

import json
import torch 
from transformers import AutoModelForCausalLM, AutoTokenizer
from xLAM_function_calling import xlam_function_calling
from tools import Tools

xlam = xlam_function_calling()

tools = Tools()

out = xlam.function_calling([], "create a file in my test directory with a poem about spring", tools.get_tools(), tools.get_available_functions())
print(out)