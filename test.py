
import copy

class OpportunutiyState():
    def __init__(self, opportunity_type, action, state, k, oop):
        self.action = action
        self.state = state
        self.k = k
        #self.state_prime = state_prime I dont need to where where i will end up
        self.opportunity = oop
        self.opportunity_type = opportunity_type

state_adj = {'s0' : ['s1.0', 's1.1'],
            's1.0' : ['s2.0'],
            's1.1' : ['s2.1'],
        #    's1.0' : ['s2.0', 's2.x'],
        #    's1.1' : ['s1.0' , 's2.1', 's2.y'],
            's2.0' : ['s3.0'],
            's2.1' : ['s3.1'],
            's2.x' : [],
            's2.y' : [],
            's3.0' : ['s4.0','s4.1'],
            's3.1' : ['s4.0', 's4.1'],
            's4.0' : [],
            's4.1' : [],
            's4.2' : []
                }

state_des = {'s0' : 0.97,
                    's1.0' : 0.3,
                    's1.1' : 0.3,
                    's2.0' : 0.96,
                    's2.1' : 0.96,
                    's2.x' : 0.94,
                    's2.y' : 0.93,
                    's3.0' : 0.96,
                    's3.1' : 0.96,
                    's4.0' : 0,
                    's4.1' : 0.4,
                    's4.2' : 0.4
                }

bnf = {}

map_benefit = {
    's0' : {
                'alpha' : 0.1,
                'beta'  : 0.5,
                'theta' : 0
            },
    's1.0' : {
                'alpha' : 0.99,
                'beta'  : 0.1,
                'theta' : 0
            },
    's1.1' : {
                'alpha' : 1,
                'beta'  : 0.1,
                'theta' : 0
            },
    's2.0' : {
                'alpha' : 0.01,
                'beta'  : 0.1,
                'theta' : 0.01
            },
    's2.1' : {
                'alpha' : 0.01,
                'beta'  : 0.1,
                'theta' : 0.01
            },
    's2.x' : {
                'alpha' : 0,
                'beta'  : 0.5,
                'theta' : 0
            },
    's2.y' : {
                'alpha' : 0,
                'beta'  : 0.5,
                'theta' : 0
            },
    's3.0' : {
                'alpha' : 0,
                'beta'  : 0.5,
                'theta' : 0
            },
    's3.1' : {
                'alpha' : 0,
                'beta'  : 0.5,
                'theta' : 0
            },
    's4.0' : {
                'alpha' : 0,
                'beta'  : 0,
                'theta' : 0
            },
    's4.1' : {
                'alpha' : 0,
                'beta'  : 0,
                'theta' : 0
            },
    's4.2' : {
                'alpha' : 0,
                'beta'  : 0,
                'theta' : 0
            },
}

def look_ahead(state_adj_map, cur_state, K):
    map_look_aheads = {}
    map_look_aheads[0] = [cur_state]
    for k in range(K):
        real_key = k+1
        map_look_aheads[real_key] = []
        for each in map_look_aheads[k]:
            linked_staes = state_adj[each]
            map_look_aheads[real_key] = [*map_look_aheads[real_key], *linked_staes]

    return copy.deepcopy(map_look_aheads)

def calculate_benefit(states, action, des_map):

    bnf = []
    map_bnf = {}
    for state in states:
    #    new_state = add_action(state)
    #    bnf.append(des_map[new_state])
        res = map_benefit[state][action]
        bnf.append(res)
        map_bnf[state] = res
    return bnf, map_bnf

def return_desirability_list(states, des_map):
    list_states_desirability = []
    for sts in states:
        list_states_desirability.append(des_map[sts])

    return copy.deepcopy(list_states_desirability)


def findOpportunity(state_adj, state_des, cur_state, action_scheme, K):
    map_look_aheads = look_ahead(state_adj, cur_state, K)
    des = state_des[cur_state]
    list_oop = []

    for each_level in map_look_aheads:
        for action in action_scheme:
            states = map_look_aheads[each_level]
            list_bnf, map_bnf = calculate_benefit(states, action, state_des)
            future_states = {}
            for each_state in states:
                future_states[each_state] = {
                    'des' : state_des[each_state],
                    'bnf' : map_bnf[each_state]
                }

            print('==========================')
            print(states)
            print('Action {}'.format(action))
            print('==========================')
            if (each_level == 0):

                oop0_alpha = oop_0(des, list_bnf)
                list_oop.append(OpportunutiyState('oop0', action, cur_state, each_level, oop0_alpha))
            else:
                oop1_alpha = oop_1(des, list_bnf)
                list_oop.append(OpportunutiyState('oop1', action, cur_state, each_level, oop1_alpha))

                oop2_alpha = oop_2(des, list_bnf)
                list_oop.append(OpportunutiyState('oop2', action, cur_state, each_level, oop2_alpha))

                oop3_alpha = oop_3(future_states)
                list_oop.append(OpportunutiyState('oop3', action, cur_state, each_level, oop3_alpha))

                oop4_alpha = oop_4(future_states)
                list_oop.append(OpportunutiyState('oop4', action, cur_state, each_level, oop4_alpha))

                des_latest_states = return_desirability_list(states, state_des)
                oop5_alpha = oop_5(des_latest_states, list_bnf)
                list_oop.append(OpportunutiyState('oop5', action, cur_state, each_level, oop5_alpha))

                oop6_alpha = oop_6(des_latest_states, list_bnf)
                list_oop.append(OpportunutiyState('oop6', action, cur_state, each_level, oop6_alpha))

        print('--------------------------------------------')
    return list_oop

# calculate action bnf
def oop_0 (des, list_bnf):
    undes = 1 - des
    bnf = min(list_bnf)
    oop = min(undes, bnf)
    print('OOP_0 Undes : {}, Bnf : {} , Oop : {}'.format(undes, bnf, oop))
    return oop

def oop_1 (des, list_bnf):
    undes = 1 - des
    bnf = max(list_bnf)
    oop = min(undes, bnf)
    print('OOP_1 Undes : {}, Bnf : {} , Oop : {}'.format(undes, bnf, oop))
    return oop

def oop_2 (des, list_bnf):
    undes = 1 - des
    bnf = min(list_bnf)
    oop = min(undes, bnf)
    print('OOP_2 Undes : {}, Bnf : {} , Oop : {}'.format(undes, bnf, oop))
    return oop

def oop_3 (future_states):
    list_oop = []
    for each_state in future_states:
        undes = 1 - future_states[each_state]['des']
        bnf = future_states[each_state]['bnf']
        list_oop.append(min(undes, bnf))
    oop = max(list_oop)
    print('OOP_3 List: {} , Oop : {}'.format(list_oop, oop))
    return oop

def oop_4 (future_states):
    list_oop = []
    for each_state in future_states:
        undes = 1 - future_states[each_state]['des']
        bnf = future_states[each_state]['bnf']
        list_oop.append(min(undes, bnf))
    oop = min(list_oop)
    print('OOP_4 List: {} , Oop : {}'.format(list_oop, oop))
    return oop

def oop_5 (des_list, list_bnf):
    list_undes = [1 - each_des for each_des in des_list]
    undes = max(list_undes)
    bnf = max(list_bnf)
    oop = min(undes, bnf)
    print('OOP_5 Undes : {}, Bnf : {} , Oop : {}'.format(undes, bnf, oop))
    return oop

def oop_6 (des_list, list_bnf):
    list_undes = [1 - each_des for each_des in des_list]
    undes = min(list_undes)
    bnf = min(list_bnf)
    oop = min(undes, bnf)
    print('OOP_6 Undes : {}, Bnf : {} , Oop : {}'.format(undes, bnf, oop))
    return oop

res = look_ahead(state_adj, 's0', 3)
print(res)

action_scheme = ['alpha', 'beta', 'theta']

list_of_res = findOpportunity(state_adj, state_des, 's0', action_scheme, 2)
