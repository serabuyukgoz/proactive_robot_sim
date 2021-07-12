from src.string_modification import *

class Opportunity():
    def __init__(self, opportunity_type, action, state, k, oop_deg):
        self.action = action
        self.state = state
        self.k = k
        #self.state_prime = state_prime I dont need to where where i will end up
        self.opportunity = oop_deg
        self.opportunity_type = opportunity_type

class OpportunityDetection():

    def __init__(self, system):
        self.sys = system

    def look_ahead(self, state_adj_map, cur_state, K):
        map_look_aheads = {}
        map_look_aheads[0] = [cur_state]
        for k in range(K):
            real_key = k+1
            map_look_aheads[real_key] = []
            for each in map_look_aheads[k]:
                linked_states = state_adj_map[each]
                map_look_aheads[real_key] = [*map_look_aheads[real_key], *linked_states]

        return copy.deepcopy(map_look_aheads)

    def calculate_bnf(self, state, action, des_map):
        '''
            Hypotetically adding action to state
            Then find the desirability of the action
        '''
        new_state_name, new_state = self.sys['emq'].add_action_to_state_name(state, action)

        if (new_state_name):
            # If the new state already known return desireability of state
            res = des_map[new_state_name]
            res = res['value']
        else:
            # If new action lead to an unknown state, calculate desireability
            res = self.sys['emq'].des.isStateDesiable(new_state)

        return res

    def calculate_benefit(self, states, action, des_map):

        bnf = []
        map_bnf = {}

        for state in states:
            res = self.calculate_bnf(state, action, des_map)
            bnf.append(res)
            map_bnf[state] = res
        return bnf, map_bnf

    def return_desirability_list(self, states, des_map):
        list_states_desirability = []
        for sts in states:
            list_states_desirability.append(des_map[sts]['value'])

        return copy.deepcopy(list_states_desirability)


    def findOpportunity(self, state_adj, state_des, cur_state_name, action_scheme, K):
        map_look_aheads = self.look_ahead(state_adj, cur_state_name, K)
        des = state_des[cur_state_name]
        list_oop = []

        for each_level in map_look_aheads:
            for action in action_scheme:
                states = map_look_aheads[each_level]
                list_bnf, map_bnf = self.calculate_benefit(states, action_scheme[action], state_des)
                future_states = {}
                for each_state in states:
                    future_states[each_state] = {
                        'des' : state_des[each_state]['value'],
                        'bnf' : map_bnf[each_state]
                    }

                if (each_level == 0):

                    oop0_alpha = self.oop_0(des['value'], list_bnf)
                    list_oop.append(Opportunity('oop0', action, cur_state_name, each_level, oop0_alpha))
                else:
                    oop1_alpha = self.oop_1(des['value'], list_bnf)
                    list_oop.append(Opportunity('oop1', action, cur_state_name, each_level, oop1_alpha))

                    oop2_alpha = self.oop_2(des['value'], list_bnf)
                    list_oop.append(Opportunity('oop2', action, cur_state_name, each_level, oop2_alpha))

                    oop3_alpha = self.oop_3(future_states)
                    list_oop.append(Opportunity('oop3', action, cur_state_name, each_level, oop3_alpha))

                    oop4_alpha = self.oop_4(future_states)
                    list_oop.append(Opportunity('oop4', action, cur_state_name, each_level, oop4_alpha))

                    des_latest_states = self.return_desirability_list(states, state_des)
                    oop5_alpha = self.oop_5(des_latest_states, list_bnf)
                    list_oop.append(Opportunity('oop5', action, cur_state_name, each_level, oop5_alpha))

                    oop6_alpha = self.oop_6(des_latest_states, list_bnf)
                    list_oop.append(Opportunity('oop6', action, cur_state_name, each_level, oop6_alpha))

        return list_oop

    # calculate action bnf
    def oop_0 (self, des, list_bnf):
        undes = 1.0 - des
        bnf = min(list_bnf)
        oop = min(undes, bnf)
        return oop

    def oop_1 ( self, des, list_bnf):
        undes = 1 - des
        bnf = max(list_bnf)
        oop = min(undes, bnf)
        #print('OOP_1 Undes : {}, Bnf : {} , Oop : {}'.format(undes, bnf, oop))
        return oop

    def oop_2 (self, des, list_bnf):
        undes = 1 - des
        bnf = min(list_bnf)
        oop = min(undes, bnf)
        #print('OOP_2 Undes : {}, Bnf : {} , Oop : {}'.format(undes, bnf, oop))
        return oop

    def oop_3 (self, future_states):
        list_oop = []
        for each_state in future_states:
            undes = 1 - future_states[each_state]['des']
            bnf = future_states[each_state]['bnf']
            list_oop.append(min(undes, bnf))
        oop = max(list_oop)
        #print('OOP_3 List: {} , Oop : {}'.format(list_oop, oop))
        return oop

    def oop_4 (self, future_states):
        list_oop = []
        for each_state in future_states:
            undes = 1 - future_states[each_state]['des']
            bnf = future_states[each_state]['bnf']
            list_oop.append(min(undes, bnf))
        oop = min(list_oop)
        #print('OOP_4 List: {} , Oop : {}'.format(list_oop, oop))
        return oop

    def oop_5 (self, des_list, list_bnf):
        list_undes = [1 - each_des for each_des in des_list]
        undes = max(list_undes)
        bnf = max(list_bnf)
        oop = min(undes, bnf)
        #rint('OOP_5 Undes : {}, Bnf : {} , Oop : {}'.format(undes, bnf, oop))
        return oop

    def oop_6 (self, des_list, list_bnf):
        list_undes = [1 - each_des for each_des in des_list]
        undes = min(list_undes)
        bnf = min(list_bnf)
        oop = min(undes, bnf)
        #print('OOP_6 Undes : {}, Bnf : {} , Oop : {}'.format(undes, bnf, oop))
        return oop

    def set_as_oop(self, intent_list, cur_state_name, cur_state, des_map, action_list,  i):
        list_oop = []
        for each_intent in intent_list:
            for each_action in intent_list[each_intent]:
                action_format = action_list[each_action]
                des = des_map[cur_state_name]['value'] - i #decreasing the desirability of the
                res = self.calculate_bnf(cur_state_name, action_format, des_map)
                bnf = res + i #increading the desirability of action effecting state_des
                oop_deg = self.oop_0(des, [bnf])
                list_oop.append(Opportunity('oop0', each_action, cur_state_name, 0, oop_deg))
        return copy.deepcopy(list_oop)
