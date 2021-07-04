import copy
import re

def return_parameter(param):
    param = param.replace("(", "")
    param = param.replace(")", "")
    param = param.replace(" -", "")
    pp = param.split(" ")
    parameter = {}

    for all in pp:
        parameter[pp.pop()] = pp.pop()

    #print(parameter)
    return copy.deepcopy(parameter)

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
    result_length = 1

    for key in parameter_map:
        result_length = result_length * len(parameter_map[key])

    #create empty array
    maped_parameter = []
    for i in range(result_length):
        maped_parameter.append({})

    for key in parameter_map:
        for index in range(result_length):
            #get right parameter to place by using offset rule (MOD)
            '''
                If 2 parameter is from same domain then it is not working!
            '''
            param_mod = index % len(parameter_map[key])
            maped_parameter[index][key] = parameter_map[key][param_mod]
    return copy.deepcopy(maped_parameter)

def turn_precondition(each_parameter, list_precon):
    new_list = []
    for precon in list_precon:
        for key in each_parameter:
            precon = re.sub(r'\s*\(\s*\)\s*', ' ', precon)
            precon = precon.replace(key, each_parameter[key])
        new_list.append(precon)
    return copy.deepcopy(new_list)

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
