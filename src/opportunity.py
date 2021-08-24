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
                if (each):
                    linked_states = state_adj_map[each]
                    map_look_aheads[real_key] = [*map_look_aheads[real_key], *linked_states]
                else:
                    print("termination state: {}".format(map_look_aheads[k]))
        print("MAP LOOK AHEAD {}".format(map_look_aheads))
        return copy.deepcopy(map_look_aheads)

    def fuction_of_K(self, K, cur_state, state_adj_map):

        next_states = []

        if(K == 0):
            next_states.append(cur_state)
            return copy.deepcopy(next_states)
        else:
            map_look_aheads = {}
            map_look_aheads[0] = [cur_state]
            for s in range(K):
                s_prime = s+1
                map_look_aheads[s_prime] = []
                for each_s in map_look_aheads[s]:
                    if (each_s):
                        linked_states = state_adj_map[each_s]
                        map_look_aheads[s_prime] = [*map_look_aheads[s_prime], *linked_states]
                    else:
                        print("termination state: {}".format(map_look_aheads[k]))
            print("MAP LOOK AHEAD of K {} : {}".format(K, map_look_aheads[K]))
            return copy.deepcopy(map_look_aheads[K])


    def bnf(self, alpha, state):
        '''
            Hypotetically adding action to state
            Then find the desirability of the action
        '''
        # Y = alpha(X)
        Y_state_name, Y_state = self.sys['emq'].add_action_to_state_name(state, alpha)

        des_y = self.sys['emq'].des.isStateDesiable(Y_state)

        print("Bnf({},{}) = {}".format(alpha, state, des_y))
        return copy.deepcopy(des_y)

    def bnf_state(self, alpha, state_des):
        '''
            Hypotetically adding action to state
            Then find the desirability of the action
        '''
        # Y = alpha(X)
        Y_state = self.sys['emq'].add_action_to_state(state_des, alpha)

        des_y = self.sys['emq'].des.isStateDesiable(Y_state)

        print("Bnf({},{}) = {}".format(alpha, state_des, des_y))
        return copy.deepcopy(des_y)


    def bnf_k(self, alpha, state, K):

        # Y = alpha(X)
        Y_state_name, Y_state = self.sys['emq'].add_action_to_state_name(state, alpha)

        # F^k of Y
        state_adj_map = self.sys['emq'].return_evolve_map()
        list_f_k = self.fuction_of_K(K, state, state_adj_map)

        des_y = []
        for each_state in list_f_k:
            state_des = self.sys['emq'].return_state_from_name(each_state)
            res_y = self.sys['emq'].des.isStateDesiable(state_des)
            des_y.append(res_y)

        # inf X elem dom(alpha, s)
        return min(des_y)

    # def calculate_bnf(self, state, action, K, state_adj):
    #     '''
    #         Hypotetically adding action to state
    #         Then find the desirability of the action
    #     '''
    #
    #     # Y = alpha(X)
    #     Y_state_name, Y_state = self.sys['emq'].add_action_to_state_name(state, action)
    #
    #     # F^k; F^0(Y) = Des(Y)
    #     # find states
    #     f_list = self.look_ahead(state_adj, Y_state_name, K)
    #
    #     # DES(states_of_F) List of states
    #     des_values = []
    #     for f_s in f_list[K] :
    #         new_state = self.sys['emq'].return_state_from_name(f_s)
    #         res = self.sys['emq'].des.isStateDesiable(new_state)
    #         des_values.append(res)
    #         print("State {} \n Desirability of {} : {}".format(state, f_s, res))
    #     return min(des_values)
    #
    # def calculate_benefit(self, states, action, des_map, state_adj, K):
    #
    #     bnf = []
    #     map_bnf = {}
    #
    #     for state in states:
    #         res = self.calculate_bnf(state, action, K, state_adj)
    #         bnf.append(res)
    #         map_bnf[state] = res
    #     return bnf, map_bnf

    def return_desirability_list(self, states, des_map):
        list_states_desirability = []
        for sts in states:
            value = self.sys['emq'].des.isStateDesiable(sts)
            list_states_desirability.append(value)

        return copy.deepcopy(list_states_desirability)


    def findOpportunity(self, state_adj, cur_state_name, action_scheme, K):
        map_look_aheads = self.look_ahead(state_adj, cur_state_name, K)
        cur_state = self.sys['emq'].return_state_from_name(cur_state_name)
        cur_state_des = self.sys['emq'].des.isStateDesiable(cur_state)
        list_oop = []

        for k in map_look_aheads:
            for action in action_scheme:
                future_states = map_look_aheads[k]

                if (k == 0):
                    bnf = self.bnf(action_scheme[action], cur_state_name)
                    oop0_alpha = self.oop_0(cur_state_des, bnf)
                    list_oop.append(Opportunity('oop0', action, cur_state_name, k, oop0_alpha))
                else:

                    list_bnf_state_prime = []
                    map_bnf_state_prime = {}
                    for each_state_prime in future_states:
                        bnf_s = self.bnf(action_scheme[action], each_state_prime)
                        list_bnf_state_prime.append(bnf_s)
                        map_bnf_state_prime[each_state_prime] = bnf_s

                    oop1_alpha = self.oop_1(cur_state_des, list_bnf_state_prime)
                    list_oop.append(Opportunity('oop1', action, cur_state_name, k, oop1_alpha))

                    oop2_alpha = self.oop_2(cur_state_des, list_bnf_state_prime)
                    list_oop.append(Opportunity('oop2', action, cur_state_name, k, oop2_alpha))

                    oop3_alpha = self.oop_3(map_bnf_state_prime)
                    list_oop.append(Opportunity('oop3', action, cur_state_name, k, oop3_alpha))

                    oop4_alpha = self.oop_4(map_bnf_state_prime)
                    list_oop.append(Opportunity('oop4', action, cur_state_name, k, oop4_alpha))

                    bnf_state_prime_k = self.bnf_k(action_scheme[action], cur_state_name, k)
                    des_latest_states = self.return_desirability_list(map_look_aheads[k])

                    oop5_alpha = self.oop_5(des_latest_states, bnf_state_prime_k)
                    list_oop.append(Opportunity('oop5', action, cur_state_name, k, oop5_alpha))

                    oop6_alpha = self.oop_6(des_latest_states, bnf_state_prime_k)
                    list_oop.append(Opportunity('oop6', action, cur_state_name, k, oop6_alpha))

        return list_oop

    # calculate action bnf
    def oop_0 (self, des, bnf):
        undes = 1.0 - des
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
            state_des = self.sys['emq'].return_state_from_name(each_state)
            des = self.sys['emq'].des.isStateDesiable(state_des)
            undes = 1 - des
            bnf = future_states[each_state]
            print('OOP_3 Details: \n state {} \n undes {} \n bnf {}'.format(each_state, undes, bnf) )
            list_oop.append(min(undes, bnf))
        oop = max(list_oop)
        print('OOP_3 List: {} , Oop : {}'.format(list_oop, oop))
        return oop

    def oop_4 (self, future_states):
        list_oop = []
        for each_state in future_states:
            state_des = self.sys['emq'].return_state_from_name(each_state)
            des = self.sys['emq'].des.isStateDesiable(state_des)
            undes = 1 - des
            bnf = future_states[each_state]
            list_oop.append(min(undes, bnf))
        oop = min(list_oop)
        #print('OOP_4 List: {} , Oop : {}'.format(list_oop, oop))
        return oop

    def oop_5 (self, des_list, bnf):
        list_undes = [1 - each_des for each_des in des_list]
        undes = max(list_undes)
        oop = min(undes, bnf)
        print('OOP_5 Undes : {}, Bnf : {} , Oop : {}'.format(undes, bnf, oop))
        return oop

    def oop_6 (self, des_list, bnf):
        list_undes = [1 - each_des for each_des in des_list]
        undes = min(list_undes)
        oop = min(undes, bnf)
        #print('OOP_6 Undes : {}, Bnf : {} , Oop : {}'.format(undes, bnf, oop))
        return oop

    # single fuction to change HiR results to opportuniti type 0
    def set_as_oop(self, intent_list, cur_state_name, cur_state, action_list,  i):
        list_oop = []
        for each_intent in intent_list:
            for each_action in intent_list[each_intent]:

                des = self.sys['emq'].des.isStateDesiable(cur_state)
                des = des - i #decreasing the desirability of the

                action_format = action_list[each_action]
                bnf_res = self.bnf_state(action_format, cur_state)
                if (bnf_res):
                    bnf = bnf_res + i #increading the desirability of action effecting state_des

                    oop_deg = self.oop_0(des, bnf)
                    list_oop.append(Opportunity('oop0', each_action, cur_state_name, 0, oop_deg))

        return copy.deepcopy(list_oop)
