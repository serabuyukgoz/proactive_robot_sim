import copy
import re
import itertools

def return_parameter(param):
#    param = param.replace("(", "")
    param = re.sub(r'\s*\(\s*', '', param)
    param = re.sub(r'\s*\)\s*', '', param)
    param = param.replace(" -", "")
    pp = param.split(" ")
    parameter = {}
    #Clear empty parameters

    order = []
    for all in pp:
        all = re.sub(r"\s+", "", all)
        if (all != ""):
            name = pp.pop(0)
            value = pp.pop(0)
            parameter[name] = value
            order.append(name)

    return copy.deepcopy(parameter), order

# precondition satisfied
def list_of_precondition(precon):
    pp = []
    if (re.findall(r'\(\s*and\s*\(', precon)):
        precon = re.sub(r'\(\s*and\s*\(', '(', precon)
        precon = re.sub(r'\s*\)\s*\)\s*', ')', precon)
        precon = re.sub(r'\)\s*\(', ');(', precon)
        pp = precon.split(";")
    else:
        pp.append(precon)
    #print(pp)
    return copy.deepcopy(pp)

# to link reach each variable as a parameter
def specify_parameters(parameter_map):
    
    list_map = []
    for key in parameter_map:
        temp = []
        for each in parameter_map[key]:
            k = {key : each}
            temp.append(k)
        list_map.append(temp)

    map = list(itertools.product(*list_map))
    create_list = []
    for all_elem in map:
        z = {}
        for i in all_elem:
            z = {**z, **i}
        create_list.append(z)
    return copy.deepcopy(create_list)

def turn_precondition(each_parameter, list_precon):
    new_list = []
    for precon in list_precon:
        for key in each_parameter:
            precon = re.sub(r'\s*\(\s*\)\s*', ' ', precon)
            precon = precon.replace(key, each_parameter[key])
        new_list.append(precon)
    return copy.deepcopy(new_list)

def findNegate(strs):
    if (re.findall(r'\(\s*not\s*\(', strs)):
        strs = re.sub(r'\(\s*not\s*', '', strs)
        strs = re.sub(r'\s*\)\s*\)\s*', ')', strs)
        return strs
    else:
        return None

def seperate_not_predicate(each_predicate):
    unwanted = []
    wanted = []
    for each in each_predicate:
        if (re.findall(r'\(\s*not\s*\(', each)):
            each = re.sub(r'\(\s*not\s*', '', each)
            each = re.sub(r'\s*\)\s*\)\s*', ')', each)
            unwanted.append(each)
        else:
        #    each = re.sub(r'\s*\(\s*\)\s*', ' ', each)
            wanted.append(each)

    return wanted, unwanted
