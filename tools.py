from default_tools import DEFAULT_TOOLS, DEFAULT_TOOLS_JSON
from helpers import get_tool_json

class Tools:
    def __init__(self):
        self.json = DEFAULT_TOOLS_JSON
        self.functions = DEFAULT_TOOLS
        
    def get_tools(self):
        """Get the tools as JSON objects"""
        return self.json
    
    def get_available_functions(self):
        """Get the available functions"""
        return self.functions
    
    def add_tool(self, function):
        self.json.append(get_tool_json(function))
        self.functions[function.__name__] = function
