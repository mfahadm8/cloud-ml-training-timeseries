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
    tree = transformer.visit(tree)
    return tree

def add_function_before_main(tree, function_name, new_function_code):
    new_function_node = ast.parse(new_function_code).body[0]
    new_body = []
    added = False

    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            if not added:
                new_body.append(new_function_node)
                added = True
        new_body.append(node)

    if not added:
        new_body.append(new_function_node)
    
    tree.body = new_body
    return tree

def replace_main_block(script_path, main_block_template_path):
    with open(script_path, 'r') as file:
        tree = ast.parse(file.read())
    
    main_block_code = read_template_function(main_block_template_path)
    main_block_node = ast.parse(main_block_code).body[0]
    
    class MainBlockTransformer(ast.NodeTransformer):
        def visit_If(self, node):
            if (isinstance(node.test, ast.Compare) and
                isinstance(node.test.left, ast.Name) and
                node.test.left.id == "__name__" and
                isinstance(node.test.ops[0], ast.Eq) and
                isinstance(node.test.comparators[0], ast.Constant) and
                node.test.comparators[0].value == "__main__"):
                return main_block_node
            return node
    
    transformer = MainBlockTransformer()
    tree = transformer.visit(tree)
    
    with open(script_path, 'w') as file:
        file.write(ast.unparse(tree))

def update_script_with_template_functions(script_path, template_functions_mapping):
    with open(script_path, 'r') as file:
        tree = ast.parse(file.read())
    
    existing_functions = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    
    for function_name, template_path in template_functions_mapping.items():
        new_function_code = read_template_function(template_path)
        if function_name in existing_functions:
            tree = replace_function_in_ast(tree, function_name, new_function_code)
        else:
            tree = add_function_before_main(tree, function_name, new_function_code)
    
    with open(script_path, 'w') as file:
        file.write(ast.unparse(tree))

