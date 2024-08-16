def convert_to_xlam_tools(tools):
    ''''''
    if isinstance(tools, dict):
        tools = tools["function"]
        return {
            "name": tools["name"],
            "description": tools["description"],
            "parameters": {k: v for k, v in tools["parameters"].get("properties", {}).items()}
        }
    elif isinstance(tools, list):
        return [convert_to_xlam_tools(tool) for tool in tools]
    else:
        return tools
    

DEFAULT_TOOLS_JSON = [
    {
        "type": "function",
        "function": {
            "name": "full_resize",
            "description": "Resize a window to the specified dimensions",
            "parameters": {
                "type": "object",
                "properties": {
                    "window_name": {
                        "type": "string",
                        "description": "The name of the window to resize"
                    },
                    "x": {
                        "type": "number",
                        "description": "The x-coordinate of the window"
                    },
                    "y": {
                        "type": "number",
                        "description": "The y-coordinate of the window"
                    },
                    "w": {
                        "type": "number",
                        "description": "The width of the window"
                    },
                    "h": {
                        "type": "number",
                        "description": "The height of the window"
                    }
                },
                "required": ["window_name", "x", "y", "w", "h"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directories",
            "description": "List all the directories in the current directory.",
            "parameters": {
                "type": "object",
                "properties": {},
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "Create a file at the given file path with the given content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path of the file to be created. Defaults to Delphi directory."
                    },
                    "content": {
                        "type": "string",
                        "description": "The content of the file."
                    }
                },
                "required": ["file_path", "content"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_text",
            "description": "Generates text given a prompt",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The prompt to generate text based on."
                    },
                },
                "required": ["prompt"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_file",
            "description": "Open the file at the given file path if it is VALID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path of the file to be opened."
                    },
                },
                "required": ["file_path"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": "Search for the file that matches query and return the file path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to search for the file. This query should be something that is semantically similar to what we are looking for.",
                    },
                },
                "required": ["query"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_application",
            "description": "Open the application with the given name. Make sure you use the correct application name for mac.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "The name of the application to be opened."
                    },
                },
                "required": ["app_name"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_applications",
            "description": "List all the applications that are currently running.",
            "parameters": {
                "type": "object",
                "properties": {},
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "close_application",
            "description": "Close the application with the given name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "The name of the application to be closed."
                    },
                },
                "required": ["app_name"],
            }
        }
    }
]



xLAM_tools = convert_to_xlam_tools(DEFAULT_TOOLS_JSON)
print(xLAM_tools)