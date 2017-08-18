"""Helper script parses *handler.py files in controller folder to list all supported
    def top_level_functions(body):
    paths in the API"""
import ast
import astunparse
import collections
from pathlib import Path

Route = collections.namedtuple('Route',
                               'filename '
                               'decorator_name '
                               'function_name '
                               'path '
                               'description '
                               'parameters '
                               'status_codes')


def flatten_attr(node):
    if isinstance(node, ast.Attribute):
        return str(flatten_attr(node.value)) + '.' + node.attr
    elif isinstance(node, ast.Name):
        return str(node.id)
    else:
        pass


def extract_routes(file, decorator_name):
    routes = []
    filename = file
    with open(file) as f:
        try:
            tree = ast.parse(f.read())
        except:
            return routes

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_name = node.name
            for d in node.decorator_list:
                if not isinstance(d, ast.Call):
                    continue
                if not flatten_attr(d.func) == decorator_name:
                    continue
                path = d.args[0].s
                description = None
                parameters = None
                status_codes = None
                for kw in d.keywords:
                    if kw.arg == 'description':
                        description = kw.value.s
                    if kw.arg == 'parameters':
                        parameters = ast.literal_eval(astunparse.unparse(kw.value))
                    if kw.arg == 'status_codes':
                        status_codes = ast.literal_eval(astunparse.unparse(kw.value))
                r = Route(filename, decorator_name, function_name, path, description, parameters,
                          status_codes)
                routes.append(r)

    return routes


def main():
    all_routes = []

    files = Path('./controller').glob('*.py')
    for file in files:
        # because path is object not string
        file_path = str(file)
        all_routes += extract_routes(file_path, 'Route.get')
        all_routes += extract_routes(file_path, 'Route.post')
        all_routes += extract_routes(file_path, 'Route.put')
        all_routes += extract_routes(file_path, 'Route.delete')

    for route in all_routes:
        print(
            f'{route.decorator_name:{12}}  {route.path:{70}} {route.description:{40}}')

if __name__ == '__main__':
    main()