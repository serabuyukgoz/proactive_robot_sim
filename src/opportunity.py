from src.string_modification import *
from print_strategy import *

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

    def look_ahead_fuction(self, state_adj_map, cur_state_object, K):
        '''
            The function gather all the futher states from each other.
        '''
        map_look_ahead = {}
        map_look_ahead[0] = [cur_state_object]

        for k in range(K):
            real_key = k+1
            map_look_ahead[real_key] = []
            for each_obj in map_look_ahead[k]:
                if (each_obj):
                    linked_states = state_adj_map[each_obj.name]
                    for each_state in linked_states:
                        # Each_state is the state Object
                        map_look_ahead[real_key].append(each_state)
        return copy.deepcopy(map_look_ahead)

    def fuction_of_K(self, K, cur_state_obj, state_adj_map):

        next_states = []

        if (cur_state_obj.name == None):
            return next_states #retrun empty states

        if(K == 0):
            next_states.append(cur_state_obj)
            return copy.deepcopy(next_states)
        else:
            map_look_aheads = {}
            map_look_aheads[0] = [cur_state_obj]

            for s in range(K):
                s_prime = s+1
                map_look_aheads[s_prime] = []
                for each_s in map_look_aheads[s]:
                    #print("... {}".format(each_s))
                    if (each_s): # if it is exist
                        if(each_s.name in state_adj_map): #if it is part of the map
                            linked_states = state_adj_map[each_s.name]
                            for each_state in linked_states:
                                map_look_aheads[s_prime].append(each_state)

            return copy.deepcopy(map_look_aheads[K])


    def bnf_calculation(self, alpha, state_obj):
        '''
            Hypotetically adding action to state
            Then find the desirability of the action
        '''

        Y_state = self.sys['emq'].add_action_to_state(state_obj.state, alpha)
        Y_state_obj = self.sys['emq'].return_object_of_state(Y_state)
        des_y = self.sys['emq'].des.stateDesirabilityValue(Y_state_obj)

        #To_debug
        des = self.sys['emq'].des.stateDesirabilityValue(state_obj)
        return copy.deepcopy(des_y), des, Y_state

    def bnf_k(self, alpha, state_obj, future_states):

        des_y = []

        #check precondirion
        check_flag = self.sys['emq'].check_precondition(state_obj.state, alpha)

        if (check_flag): #action applicable to the

            for each_state_obj in future_states:
                #add action
                des_prime = self.sys['emq'].des.stateDesirabilityValue(each_state_obj)
                Y_state = self.sys['emq'].add_action(each_state_obj.state, alpha)
                Y_state_obj = self.sys['emq'].return_object_of_state(Y_state)
                Y_des = self.sys['emq'].des.stateDesirabilityValue(Y_state_obj)

                des_y.append(Y_des)

        if (des_y == []):
            return 0
        else:
            return min(des_y)

    def return_desirability_list(self, states):
        list_states_desirability = []
        for sts in states:
            value = self.sys['emq'].des.stateDesirabilityValue(sts)
            list_states_desirability.append(value)

        return copy.deepcopy(list_states_desirability)


    def findOpportunity(self, state_adj, cur_state, action_scheme, K):

        if (cur_state == []):
            raise Exception("Current State is Empty = []")

        cur_state_object = self.sys['emq'].return_object_of_state(cur_state)

        # cur_state_des = self.sys['emq'].des.stateDesirabilityValue(cur_state)
        map_look_aheads = self.look_ahead_fuction(state_adj, cur_state_object, K)

        list_oop = []

        for k in map_look_aheads:
            for action in action_scheme:
                future_states = map_look_aheads[k]

                if (k == 0):
                    bnf, dy, sy = self.bnf_calculation(action_scheme[action], future_states[0])
                    cur_state_des = self.sys['emq'].des.stateDesirabilityValue(future_states[0])
                    oop0_alpha = self.oop_0(cur_state_des, bnf)
                    print("Opp 0 ({}, {}, {}) = {} \n \t Des: {} \n \t BNF: {} ".format(cur_state_object.name, action, k, oop0_alpha, cur_state_des, bnf))
                    list_oop.append(Opportunity('oop0', action, cur_state_object.name, k, oop0_alpha))

                else:
                    # For opp 1 and 2
                    list_bnf_state_prime = []
                    for each_state_prime in future_states:
                        bnf_s, dy, sy = self.bnf_calculation(action_scheme[action], each_state_prime)
                        list_bnf_state_prime.append(bnf_s)

                    oop1_alpha = self.oop_1(cur_state_des, list_bnf_state_prime)
                    print("Opp 1 ({}, {}, {}) = {} \n \t Des: {} \n \t BNF: {} ".format(cur_state_object.name, action, k, oop1_alpha, cur_state_des, list_bnf_state_prime))
                    list_oop.append(Opportunity('oop1', action, cur_state_object.name, k, oop1_alpha))

                    oop2_alpha = self.oop_2(cur_state_des, list_bnf_state_prime)
                    print("Opp 2 ({}, {}, {}) = {} \n \t Des: {} \n \t BNF: {} ".format(cur_state_object.name, action, k, oop2_alpha, cur_state_des, list_bnf_state_prime))
                    list_oop.append(Opportunity('oop2', action, cur_state_object.name, k, oop2_alpha))

                    oop3_alpha = self.oop_3(future_states, action_scheme[action])
                    list_oop.append(Opportunity('oop3', action, cur_state_object.name, k, oop3_alpha))

                    oop4_alpha = self.oop_4(future_states, action_scheme[action])
                    list_oop.append(Opportunity('oop4', action, cur_state_object.name, k, oop4_alpha))

                    # #More detail for calculate other opportunuties
                    # bnf_state_prime_k = self.bnf_k(action_scheme[action], cur_state_object, k)
                    des_latest_states = self.return_desirability_list(map_look_aheads[k])
                    bnf_state_prime_k = self.bnf_k(action_scheme[action], cur_state_object, map_look_aheads[k])

                    oop5_alpha = self.oop_5(des_latest_states, bnf_state_prime_k)
                    list_oop.append(Opportunity('oop5', action, cur_state_object.name, k, oop5_alpha))

                    oop6_alpha = self.oop_6(des_latest_states, bnf_state_prime_k)
                    list_oop.append(Opportunity('oop6', action, cur_state_object.name, k, oop6_alpha))

        return list_oop

    # calculate action bnf
    def oop_0 (self, des, bnf):
        undes = 1.0 - des
        oop = min(undes, bnf)
        return oop

    def oop_1 ( self, des, list_bnf):
        undes = 1 - des
        try:
            if (list_bnf):
                bnf = max(list_bnf)
            else:
                bnf = 0
            oop = min(undes, bnf)
            return oop
        except:
            raise Exception("OOP_1 Undes : %s, Bnf : %s" %(undes, list_bnf))

    def oop_2 (self, des, list_bnf):
        undes = 1 - des
        if (list_bnf):
            bnf = min(list_bnf)
        else:
            bnf = 0
        oop = min(undes, bnf)
        return oop


    def oop_3 (self, future_states, action):
        list_oop = []
        for each_state in future_states:
            des = self.sys['emq'].des.stateDesirabilityValue(each_state)
            undes = 1 - des
            bnf, dy, sy = self.bnf_calculation(action, each_state)
            list_oop.append(min(undes, bnf))
        if(list_oop):
            oop = max(list_oop)
        else:
            oop = 0
        return oop

    def oop_4 (self, future_states, action):
        list_oop = []
        for each_state in future_states:
            des = self.sys['emq'].des.stateDesirabilityValue(each_state)
            undes = 1 - des
            bnf, dy, sy = self.bnf_calculation(action, each_state)
            list_oop.append(min(undes, bnf))
        if(list_oop):
            oop = min(list_oop)
        else:
            oop = 0
        return oop

    def oop_5 (self, des_list, bnf):
        if(des_list):
            list_undes = [1 - each_des for each_des in des_list]
            undes = max(list_undes)
            oop = min(undes, bnf)
            return oop
        else:
            return 0

    def oop_6 (self, des_list, bnf):
        if(des_list):
            list_undes = [1 - each_des for each_des in des_list]
            undes = min(list_undes)
            oop = min(undes, bnf)
            return oop
        else:
            return 0

    # single fuction to change HiR results to opportuniti type 0
    def set_as_oop(self, intented_action, cur_state, action_list,  i):
        if (cur_state == []):
            raise Exception("Current State is Empty = []")

        cur_state_obj = self.sys['emq'].return_object_of_state(cur_state)

        des = self.sys['emq'].des.stateDesirabilityValue(cur_state_obj)
        des = des - i #decreasing the desirability of the
        if (des < 0):
            des = 0

        action_format = action_list[intented_action]
        bnf_res, d, y  = self.bnf_calculation(action_format, cur_state_obj)
        bnf = bnf_res + i #increading the desirability of action effecting state_des
        if (bnf > 1.0):
            bnf = 1.0

        oop_deg = self.oop_0(des, bnf)

        return [Opportunity('oop0', intented_action, cur_state_obj.name, 0, oop_deg)]
