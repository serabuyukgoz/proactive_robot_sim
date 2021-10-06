def print_all(react, opp, opp_int, system):
    print("-----------------------------------------------")
    print("Reaction time in millisec %s" %react )
    print("--- For Equilibrium Maintenance ----")
    #return desirability Function
    #print("Desirability Function -> %s " %(system['recogniser'].return_desirability_value()))
    #return current state
    separator = '  \n '
    cur_state = system['env'].return_current_state()
    cur_state_obj = system['emq'].return_object_of_state(cur_state)
    print("Current State -> \n %s" %(cur_state_obj.name))
    #return state evolvation
    print("State Evolvation -> ")
    #print_dict(system['env'].return_state_evolution())
    #return action list
    #act_list = system['env'].return_action_list()
    act_list = system['env'].return_unvoluntary_action_list()
    print("Action List ->")
    print_act(act_list)
    act_scheme = system['env'].return_robot_action_list()
    print("Robot Action Scheme List ->")
    print_robot_act(act_scheme)
    print("Opp List from Intention Recognition ->")
    print_oop(opp_int)
    print("Opp List ->")
    print_oop(opp)

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

def print_robot_act(dct):
    for item, amount in dct.items():
        print(" + {}".format(item))
        print(" \t Precondition : {} \n \t Effect : {}".format(amount['precondition'], amount['effect']))

def print_oop(dct):
    for item in dct:
        if (item.opportunity > 0.0):
            print(" {}({}, {}, {}) = {}".format(item.opportunity_type, item.action, item.state, item.k, item.opportunity))

def print_des(dct):
    print("Desireability Function ->")
    for item, amount in dct.items():
        print(" == {} : ".format(item))
        for i, a in amount.items():
            print(" \t {} : ".format(i))
            print(" \t \t State : {} ".format(a['state']))
            print(" \t \t Desireability Value : {} ".format(a['value']))

def print_evolve_map(dct):
    for item, amount in dct.items():
        print(" -- {} :".format(item))
        for a in amount:
            print(" \t -> {} = {} ".format(a.name, a.desirability))

def print_hash_map(dct):
    for item, a in dct.items():
        print(" ++ {} :".format(item))
        print(" \t Name = {} \n \t State = {} \n \t Des = {} ".format(a.name, a.state, a.desirability))
