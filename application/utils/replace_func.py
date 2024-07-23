import ast
import os


def read_template_function(template_path):
    with open(template_path, 'r') as file:
        return file.read()

def replace_function_in_ast(tree, function_name, new_function_code):
    new_function_node = ast.parse(new_function_code).body[0]
    
    class FunctionTransformer(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            if node.name == function_name:
                return new_function_node
            return node
    
    transformer = FunctionTransformer()
    return transformer.visit(tree)

def update_script_with_template_functions(script_path,template_functions_mapping):
    with open(script_path, 'r') as file:
        tree = ast.parse(file.read())
    
    for function_name, template_path in template_functions_mapping.items():
        new_function_code = read_template_function(template_path)
        tree = replace_function_in_ast(tree, function_name, new_function_code)
    
    with open(script_path, 'w') as file:
        file.write(ast.unparse(tree))

    
    (script_path)
