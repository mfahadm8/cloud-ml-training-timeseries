import ast
import pandas as pd

required_functions = ["main"]

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

def get_annotation_id(annotation):
    if isinstance(annotation, ast.Name):
        return annotation.id
    elif isinstance(annotation, ast.Attribute):
        return annotation.attr
    elif isinstance(annotation, ast.Subscript):
        return get_annotation_id(annotation.value)
    else:
        return None

def check_main_arguments(tree):
    expected_args = {
        "chars": "DataFrame",
        "features": "DataFrame",
        "daily_ret": "DataFrame"
    }
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            args = {arg.arg: get_annotation_id(arg.annotation) if arg.annotation else None for arg in node.args.args}
            missing_args = [arg for arg in expected_args if arg not in args]
            if missing_args:
                return False, f"Missing arguments in 'main': {', '.join(missing_args)}"
            
            for arg, expected_type in expected_args.items():
                if args[arg] != expected_type:
                    return False, f"Argument '{arg}' should be of type '{expected_type}', found '{args[arg]}'"
    return True, ""

def check_main_return_type(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            for stmt in node.body:
                if isinstance(stmt, ast.Return):
                    # Checking if the return type is a DataFrame
                    # Note: This is a simple check, and more sophisticated type inference might be required
                    return_expr = ast.dump(stmt.value)
                    if "pf" not in return_expr:
                        return False, "The 'main' function should return a pf"
    return True, ""

def perform_static_checks(file_path):
    syntax_ok, result = check_syntax(file_path)
    if not syntax_ok:
        return False, f"Syntax Error: {result}"
    
    tree = result
    missing_functions = check_required_functions(tree)
    if missing_functions:
        return False, f"Missing required functions: {', '.join(missing_functions)}"
    
    args_ok, args_result = check_main_arguments(tree)
    if not args_ok:
        return False, args_result
    
    return_ok, return_result = check_main_return_type(tree)
    if not return_ok:
        return False, return_result
    
    return True, "Static checks passed"
