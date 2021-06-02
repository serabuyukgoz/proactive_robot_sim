def print_all(react, system):
    print("-----------------------------------------------")
    print("Reaction time in millisec %s" %react )
    print("--- For Equilibrium Maintenance ----")
    #return desirability Function
    #print("Desirability Function -> %s " %(system['recogniser'].return_desirability_value()))
    #return current state
    separator = '  \n '
    print("Current State -> \n %s" %(separator.join(system['env'].return_current_state())))
    #return state evolvation
    print("State Evolvation -> ")
    print_dict(system['env'].return_state_evolution())
    #return action list
    act_list = system['env'].return_action_list()
    print("Action List ->")
    print_act(act_list)

    print("-----------------------------------------------")

def print_dict(dct):
    separator = ' \n '
    for item, amount in dct.items():
        print(" -- {} : \n ".format(item))
        for i, a in amount.items():
            print(" \t {} : ".format(i))
            for element in a:
                print(" \t \t {} ".format(element))


def print_act(dct):
    for item, amount in dct.items():
        print(" ** {}".format(item))
        print(" \t Name : {}  \n \t Parameter : {} \n \t Precondition : {} \n \t Effect : {}".format(amount.name, amount.parameter, amount.precondition, amount.effect))

def print_des(dct):
    for item, amount in dct.items():
        print(" == {} : ".format(item))
        for i in amount.items():
            print(i)
