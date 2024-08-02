import sympy as sp

# Function to calculate the definite integral

def integral_solver(expr, var, lower_limit, upper_limit):
    # Define the variable
    variable = sp.symbols(var)
    
    # Parse the expression
    expression = sp.sympify(expr)
    
    # Calculate the definite integral
    integral = sp.integrate(expression, (variable, lower_limit, upper_limit))
    
    return integral

# Example usage
if __name__ == '__main__':
    expr = 'x**2'
    var = 'x'
    lower_limit = 0
    upper_limit = 1
    result = integral_solver(expr, var, lower_limit, upper_limit)
    print(f'The integral of {expr} from {lower_limit} to {upper_limit} is: {result}')