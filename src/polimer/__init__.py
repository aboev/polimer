# Copyright, Aleksey Boev 2024

import sys, inspect
from collections import deque
from copy import deepcopy
from types import ModuleType

def load_functions():
    functions = {}
    for module_name in sys.modules:
        for item in vars(sys.modules[module_name]).values():
            if (inspect.isfunction(item) == True) and (len(item.__annotations__) > 0):
                f_id = item.__module__ + "." + item.__name__
                functions[f_id] = item
    return functions

def build_dep_tree(functions):
    f_ids = {} # artifact_id -> function_id map
    dep_tree = {}
    for f_id in functions:
        artifact_id = functions[f_id].__annotations__.get("return", None)
        if artifact_id != None: f_ids[artifact_id] = f_id
    for f_id in functions:
        dep_tree[f_id] = []
        annotations = functions[f_id].__annotations__
        for argument in annotations:
            dep_artifact_id = annotations[argument]
            dep_f_id = f_ids.get(dep_artifact_id, None)
            if (argument != "return") and (dep_f_id != None):
                dep_tree[f_id].append(dep_f_id)
    return dep_tree

def topology_sort(dep_tree, start_f_id):
    res_deque = deque()
    visited = set()
    stack = [[start_f_id]]
    while stack:
        for f_id in stack[-1]: 
            if (f_id in visited) and (f_id not in res_deque): 
                res_deque.appendleft(f_id)
            if f_id not in visited:
                visited.add(f_id)
                stack.append(dep_tree[f_id]) 
                break
        else: 
            stack.pop()
    result = list(res_deque)
    result.reverse()
    return result

def prepare_kwargs(function, artifacts, kwargs):
    result = {}
    spec = inspect.getfullargspec(function)
    annotations = function.__annotations__
    for argument in spec.args:
        artifact_id = annotations.get(argument, None)
        if argument in kwargs:
            result[argument] = kwargs[argument]
        elif artifact_id in artifacts:
            result[argument] = artifacts[artifact_id]
    return result

def run_chain(chain, functions, kwargs):
    result = None
    artifacts = {}
    for f_id in chain:
        res = functions[f_id](**prepare_kwargs(functions[f_id], artifacts, kwargs))
        artifact_id = functions[f_id].__annotations__.get("return", None)
        if artifact_id != None: artifacts[artifact_id] = res
        result = res
    return result

def run(f_id, user_kwargs):
    functions = load_functions()
    dep_tree = build_dep_tree(functions)
    chain = topology_sort(dep_tree, f_id)
    return run_chain(chain, functions, user_kwargs)

def get_func(f_id):
    def func(**kwargs):
        return run(f_id, kwargs)
    return func

functions = load_functions()
__all__ = []

for f_id in functions:
    module_name, function_name = f_id.split(".", 1)
    if module_name not in globals():
        globals()[module_name] = ModuleType(module_name)
        __all__.append(module_name)
    setattr(globals()[module_name], function_name, deepcopy(get_func(f_id)))

__all__ = tuple(__all__)
