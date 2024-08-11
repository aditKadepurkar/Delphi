from function_calling import function_caller
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
class gpt_function_caller(function_caller):
    def __init__(self):
        load_dotenv()
        os.getenv("OPENAI_API_KEY")
        self.client = OpenAI()
    def set_func(self, func):
        pass

    def function_calling(self, messages, tools, available_functions):
        """Calls one iteration of the function calling process."""
        
        # Get the response
        response = self.client.chat.completions.create(
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