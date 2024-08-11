from default_tools import DEFAULT_TOOLS

class tools:
    def __init__(self):
        self.tools = DEFAULT_TOOLS
        
    def get_tools(self):
        pass
    
    def add_tool(self, function):
        json = get_tool_json(function)
        self.tools.append(json)