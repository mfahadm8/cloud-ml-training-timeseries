import ast
import os

required_functions = ["ecdf", "prepare_data", "fit_xgb", "load_data", "export_data", "main"]

def check_syntax(file_path):
    try:
        with open(file_path, "r") as file:
            tree = ast.parse(file.read())
        return True, tree
    except SyntaxError as e:
        return False, str(e)

def check_required_functions(tree):
    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    missing_functions = [func for func in required_functions if func not in functions]
    return missing_functions

def check_no_nested_functions(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for inner_node in ast.walk(node):
                if isinstance(inner_node, ast.FunctionDef):
                    if inner_node != node:
                        return False, f"Nested function {inner_node.name} found in {node.name}"
    return True, ""

def perform_static_checks(file_path):
    syntax_ok, result = check_syntax(file_path)
    if not syntax_ok:
        return False, f"Syntax Error: {result}"
    
    tree = result
    missing_functions = check_required_functions(tree)
    if missing_functions:
        return False, f"Missing required functions: {', '.join(missing_functions)}"
    
    nested_ok, nested_result = check_no_nested_functions(tree)
    if not nested_ok:
        return False, nested_result
    
    return True, "Static checks passed"

# Example usage
file_path = "submitted_script.py"
is_valid, message = perform_static_checks(file_path)
print(message)
