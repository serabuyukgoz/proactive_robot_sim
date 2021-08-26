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

    def look_ahead_fuction(self, state_adj_map, cur_state, K):
        map_look_aheads = {}
        map_look_aheads[0] = [cur_state]
        for k in range(K):
            real_key = k+1
            map_look_aheads[real_key] = []
            for each in map_look_aheads[k]:
                if (each):
                    linked_states = state_adj_map[each]
                    map_look_aheads[real_key] = [*map_look_aheads[real_key], *linked_states]
                    #print("map_look_aheads: {}".format(map_look_aheads))
                else:
                    print("termination state: {}".format(map_look_aheads[k]))
        print("MAP LOOK AHEAD {}".format(map_look_aheads))
        return copy.deepcopy(map_look_aheads)

    def fuction_of_K(self, K, cur_state, state_adj_map):

        next_states = []

        if (cur_state == None):
            return next_states #retrun empty states

        if(K == 0):
            next_states.append(cur_state)
            return copy.deepcopy(next_states)
        else:
            map_look_aheads = {}
            map_look_aheads[0] = [cur_state]
            print(". {}".format(cur_state))
            for s in range(K):
                print(".. {} / {} ".format(s, K))
                s_prime = s+1
                map_look_aheads[s_prime] = []
                for each_s in map_look_aheads[s]:
                    print("... {}".format(each_s))
                    if (each_s):
                        linked_states = state_adj_map[each_s]
                        map_look_aheads[s_prime] = [*map_look_aheads[s_prime], *linked_states]
                    else:
                        print("termination state function K: {}".format(map_look_aheads[K]))
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

        # return copy.deepcopy(des_y)

        #To_debug
        state_des = self.sys['emq'].return_state_from_name(state)
        des = self.sys['emq'].des.isStateDesiable(state_des)
        return copy.deepcopy(des_y), des, Y_state

    def bnf_state(self, alpha, state_des):
        '''
            Hypotetically adding action to state
            Then find the desirability of the action
        '''
        # Y = alpha(X)
        Y_state = self.sys['emq'].add_action_to_state(state_des, alpha)

        des_y = self.sys['emq'].des.isStateDesiable(Y_state)

        return copy.deepcopy(des_y)

        #To_debug
        state_des = self.sys['emq'].return_state_from_name(state)
        des = self.sys['emq'].des.isStateDesiable(state_des)
        return copy.deepcopy(des_y), des, Y_state


    def bnf_k(self, alpha, state, K):

        #To_debug
        state_name = self.sys['emq'].return_state_from_name(state)
        des = self.sys['emq'].des.isStateDesiable(state_name)
        print("How to set BNF(a,s,k): \n \t Action : %s  \n \t state : %s \n \t State Des: %s \n \t K : %s" %(alpha['name'], state_name, des, K))

        # Y = alpha(X)
        Y_state_name, Y_state = self.sys['emq'].add_action_to_state_name(state, alpha)
        print("\t Y_state: %s - %s " %(Y_state_name, Y_state))

        if(Y_state == []):
            print(" \t bnf : 0 (action not applicable - no further state) ")
            print("-------------------------------------")
            return 0

        # F^k of Y
        state_adj_map = self.sys['emq'].return_evolve_map()
        list_f_k = self.fuction_of_K(K, Y_state_name, state_adj_map)
        print("\t Prime States of Y -> %s" %list_f_k)
        des_y = []
        for each_state in list_f_k:
            each_state_name = self.sys['emq'].return_state_from_name(each_state)
            res_y = self.sys['emq'].des.isStateDesiable(each_state_name)
            des_y.append(res_y)
            print(" \t state_prime : %s \n \t s_prime des : %s " %(each_state_name, res_y))

        # inf X elem dom(alpha, s)

        if (des_y == []):
            print(" \t min_bnf zero : 0 ")
            print("-------------------------------------")
            return 0
        else:
            print(" \t min_bnf : %s " %(min(des_y)))
            print("-------------------------------------")
            return min(des_y)


    def return_desirability_list(self, states):
        list_states_desirability = []
        for sts in states:
            value = self.sys['emq'].des.isStateDesiable(sts)
            list_states_desirability.append(value)

        return copy.deepcopy(list_states_desirability)


    def findOpportunity(self, state_adj, cur_state_name, action_scheme, K):

        if (cur_state_name == "(Empty)"):
            raise Exception("Current State is Empty = []")

        cur_state = self.sys['emq'].return_state_from_name(cur_state_name)

        cur_state_des = self.sys['emq'].des.isStateDesiable(cur_state)
        map_look_aheads = self.look_ahead_fuction(state_adj, cur_state_name, K)

        list_oop = []

        for k in map_look_aheads:
            for action in action_scheme:
                future_states = map_look_aheads[k]

                if (k == 0):
                    bnf, dy, sy = self.bnf(action_scheme[action], cur_state_name)
                    print("How to set BNF(a,s): \n \t BNF (DES_of_y) : %s \n \t DES : %s \n \t DES_of_prime : %s \n \tAction : %s \n \t State Y : %s \n \t State Prime : %s \n \t State : %s \n \t K : %s " %(str(bnf), str(cur_state_des), dy, action_scheme[action]['name'], sy, cur_state_name, cur_state_name, str(k)))
                    print("-------------------------------------")
                    oop0_alpha = self.oop_0(cur_state_des, bnf)
                    list_oop.append(Opportunity('oop0', action, cur_state_name, k, oop0_alpha))

                else:
                    list_bnf_state_prime = []
                    map_bnf_state_prime = {}
                    for each_state_prime in future_states:
                        bnf_s, dy, sy = self.bnf(action_scheme[action], each_state_prime)
                        print("How to set BNF(a,s): \n \t BNF (DES_of_y) : %s \n \t DES : %s \n \t DES_of_prime : %s \n \tAction : %s \n \t State Y : %s \n \t State Prime : %s \n \t State : %s \n \t K : %s " %(str(bnf_s), str(cur_state_des), dy, action_scheme[action]['name'], sy, each_state_prime, cur_state_name, str(k)))
                        print("-------------------------------------")
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

                    # #More detail for calculate other opportunuties
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
        try:
            bnf = max(list_bnf)
            oop = min(undes, bnf)
            #print('OOP_1 Undes : {}, Bnf : {} , Oop : {}'.format(undes, bnf, oop))
            return oop
        except:
            raise Exception("OOP_1 Undes : %s, Bnf : %s" %(undes, list_bnf))

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
            #print('OOP_3 Details: \n state {} \n undes {} \n bnf {}'.format(each_state, undes, bnf) )
            list_oop.append(min(undes, bnf))
        oop = max(list_oop)
        #print('OOP_3 List: {} , Oop : {}'.format(list_oop, oop))
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
        #print('OOP_5 Undes : {}, Bnf : {} , Oop : {}'.format(undes, bnf, oop))
        return oop

    def oop_6 (self, des_list, bnf):
        list_undes = [1 - each_des for each_des in des_list]
        undes = min(list_undes)
        oop = min(undes, bnf)
        #print('OOP_6 Undes : {}, Bnf : {} , Oop : {}'.format(undes, bnf, oop))
        return oop

    # single fuction to change HiR results to opportuniti type 0
    def set_as_oop(self, intent_list, cur_state_name, cur_state, action_list,  i):
        if (cur_state == []):
            raise Exception("Current State is Empty = []")

        list_oop = []
        for each_intent in intent_list:
            #for each_action in intent_list[each_intent]:
            each_action = intent_list[each_intent][0]
            des = self.sys['emq'].des.isStateDesiable(cur_state)
            des = des - i #decreasing the desirability of the

            action_format = action_list[each_action]
            bnf_res = self.bnf_state(action_format, cur_state)
            if (bnf_res):
                bnf = bnf_res + i #increading the desirability of action effecting state_des

                oop_deg = self.oop_0(des, bnf)
                list_oop.append(Opportunity('oop0', each_action, cur_state_name, 0, oop_deg))
            else:
                raise Exception("BNF None in set opportunity for HiR \n More detail -> \n cur_state_name %s \n cur_state %s \n action %s \n des of state %s \n bnf %s" %(cur_state_name, cur_state, each_action, des, bnf_res))

        return copy.deepcopy(list_oop)
