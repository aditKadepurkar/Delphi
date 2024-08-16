

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

torch.random.manual_seed(0) 

import torch


device = torch.device("cpu") # Required on MACOS as far as I can tell. MPS device always breaks.

# model = model.to(device)
# input_tensor = input_tensor.to(device)


model_name = "Salesforce/xLAM-1b-fc-r"
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto", torch_dtype="auto", trust_remote_code=True)
model = model.to(device)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Please use our provided instruction prompt for best performance
task_instruction = """
You are an expert in composing functions. You are given a question and a set of possible functions. 
Based on the question, you will need to make one or more function/tool calls to achieve the purpose. 
If none of the functions can be used, point it out and refuse to answer. 
If the given question lacks the parameters required by the function, also point it out.
""".strip()

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

# Define the input query and available tools
query = "What's the weather like in New York in fahrenheit?"

get_weather_api = {
    "name": "get_weather",
    "description": "Get the current weather for a location",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city and state, e.g. San Francisco, New York"
            },
            "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "The unit of temperature to return"
            }
        },
        "required": ["location"]
    }
}

search_api = {
    "name": "search",
    "description": "Search for information on the internet",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query, e.g. 'latest news on AI'"
            }
        },
        "required": ["query"]
    }
}

openai_format_tools = [get_weather_api, search_api]

# Helper function to convert openai format tools to our more concise xLAM format
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

# Helper function to build the input prompt for our model
def build_prompt(task_instruction: str, format_instruction: str, tools: list, query: str):
    prompt = f"[BEGIN OF TASK INSTRUCTION]\n{task_instruction}\n[END OF TASK INSTRUCTION]\n\n"
    prompt += f"[BEGIN OF AVAILABLE TOOLS]\n{json.dumps(xlam_format_tools)}\n[END OF AVAILABLE TOOLS]\n\n"
    prompt += f"[BEGIN OF FORMAT INSTRUCTION]\n{format_instruction}\n[END OF FORMAT INSTRUCTION]\n\n"
    prompt += f"[BEGIN OF QUERY]\n{query}\n[END OF QUERY]\n\n"
    return prompt
    
# Build the input and start the inference
xlam_format_tools = convert_to_xlam_tool(openai_format_tools)
content = build_prompt(task_instruction, format_instruction, xlam_format_tools, query)

messages=[
    { 'role': 'user', 'content': content}
]
inputs = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt").to(model.device)
print(inputs)

# tokenizer.eos_token_id is the id of <|EOT|> token
outputs = model.generate(inputs, max_new_tokens=512, do_sample=False, num_return_sequences=1, eos_token_id=tokenizer.eos_token_id)
print(tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True))

