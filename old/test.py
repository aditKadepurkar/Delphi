def get_tool_json(function):
    name = function.__name__
    arg_count = function.__code__.co_argcount
    params = function.__code__.co_varnames
    desc = function.__doc__
    
    print(name)
    print(arg_count)
    print(params)
    print(desc)
    
    
def real(input, bizz):
    """
    text that is the summary

    @param param_1: type1: desc
    @return: type2: desc
    """
    pass

get_tool_json(real)