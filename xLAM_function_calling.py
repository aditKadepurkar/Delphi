from function_calling import function_caller
import json
import torch 
from transformers import AutoModelForCausalLM, AutoTokenizer
from defaults import TASK_INSTRUCTION_XLAM, FORMAT_INSTRUCTION_XLAM
from helpers import convert_to_xlam_tools

class xlam_function_calling(function_caller):
    def __init__(self):
        torch.random.manual_seed(0) 
        model_name = "Salesforce/xLAM-1b-fc-r"
        self.model = AutoModelForCausalLM.from_pretrained(model_name, device_map="cpu", torch_dtype="auto", trust_remote_code=True)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.task_instruction = TASK_INSTRUCTION_XLAM
        self.format_instruction = FORMAT_INSTRUCTION_XLAM
        self.device = torch.device("cpu")

    def set_func(self, func):
        pass

    def function_calling(self, messages, query, tools, available_functions):
        tools = convert_to_xlam_tools(tools)
        prompt = f"[BEGIN OF TASK INSTRUCTION]\n{self.task_instruction}\n[END OF TASK INSTRUCTION]\n\n"
        prompt += f"[BEGIN OF AVAILABLE TOOLS]\n{json.dumps(tools)}\n[END OF AVAILABLE TOOLS]\n\n"
        prompt += f"[BEGIN OF FORMAT INSTRUCTION]\n{self.format_instruction}\n[END OF FORMAT INSTRUCTION]\n\n"
        prompt += f"[BEGIN OF QUERY]\n{query}\n[END OF QUERY]\n\n"

        messages.append(
            { 'role': 'user', 'content': prompt}
        )
        
        inputs = self.tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt").to(self.device)
        
        outputs = self.model.generate(inputs, max_new_tokens=512, do_sample=False, num_return_sequences=1, eos_token_id=self.tokenizer.eos_token_id)
        
        response_message = self.tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)
        print(response_message)
        tool_calls = json.loads(response_message)["tool_calls"]
        
        if tool_calls:
            messages.append(response_message)
            for tool_call in tool_calls:
                function_name = tool_call["name"]
                function = available_functions[function_name]
                parameters = tool_call["arguments"]
                
                func_response = function(
                    **parameters
                )

                messages.append(
                    {
                        "role": "tool",
                        "name": function_name,
                        "content": func_response,
                    }
                )
            return messages
        return "Failed"