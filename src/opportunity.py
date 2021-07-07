from src.string_modification import *

class Opportunity():
    def __init__(self, opportunity_type, action, state, k, oop):
        self.action = action
        self.state = state
        self.k = k
        #self.state_prime = state_prime I dont need to where where i will end up
        self.opportunity = oop
        self.opportunity_type = opportunity_type

class OpportunityDetection():

    def __init__(self, system):
        self.sys = system

    def checkAllOpportunitues(self, opportunity_map, action_list):
        print("++++ CHECK ALL OPPORTUNITIES ++++")
        list_of_oppotunities = {}

        for t in opportunity_map:
            list_of_oppotunities[t] = []
            for state_des in opportunity_map[t]:
                print(opportunity_map[t][state_des])
                oop = self.opp(opportunity_map[t][state_des],action_list)
                print("opportunity")
                print(oop)
                if (oop):
                    list_of_oppotunities[t].append(oop)
                else:
                    print("No opportunity found")

        print("Detected Opportuniy Map -> {}".format(list_of_oppotunities))
        return list_of_oppotunities

    def opp(self, status, action_list):
        '''
            Check opportunities that for states is not desirable
            state value != 1.0

            This is a wrong statement, because it is important to also check how action
            degregade the desirability of the state. Then, actually it is not an opportunity.
            Maybe to tell not to plat this?
            Just to see on the data?

        '''
        list_of_opportunities_for_state = {}
        #if (status['value'] != 1.0): #if it is not maximum desirability
        #for all action add and try to see the
        for a in action_list:
            # a is name of the action
            next_state = self.add_action(status['state'],action_list[a])
            #if it is exists
            if (next_state):
                oppo = Opportunity(status['state'], action_list[a], next_state['state'], status['value'], next_state['value'] )
                list_of_opportunities_for_state[a] = oppo

        print("list of opportunuties")
        print(list_of_opportunities_for_state)
        return list_of_opportunities_for_state

    def add_action(self, state, action):

        #from the map check where it could go
        #from the current state

        #check if action precondion maped_temp
        next_state = self.sys['env'].add_action_to_state(state, action)
        des_value = self.sys['des'].isStateDesiable(next_state)

        #next_state = []
        #des_value = -1

        if (next_state):
            print("NEXT STATE {}".format(next_state))
            print("des_value {}".format(des_value))
            return {'state': next_state, 'value' : des_value}
        else:
            print("THERE IS NO NEXT STATE")
            return 0

    def calculate_benefit_of_iterating(evolve_map, des):
        '''
            Calculating Benefit of moving one state to another
        '''
        bnf_map = {}

        for each_state in evolve_map:
            each_state_des = des[each_state]
            for each_next_state in evolve_map[each_state]:
                name_next_state = each_state[1]
                pos_next_state_des = des[name_next_state]
                bnf_map[name_cur_state][each_state] = pos_next_state_des - each_state_des

        return copy.deepcopy(bnf_map)

    def benefit_calculation(self, state, state_prime, des):
        bnf_deg = des[state_prime] - des[state]
        return bnf_deg


    def findOpportunity(self, cur_state, des, evolve_map, hashmap_state, action_sheme):

        name_cur_state = check_in_map(hashmap_state, cur_state)
        curent_state_des = des[name_cur_state]
        next_state = evolve_map[name_cur_state] #list of next state could be reached

        bnf_map_free_run = self.calculate_benefit_of_iterating(evolve_map, des)

        if (curent_state_des < 1.0):
            #1 time look ahead
            for each_possible_state in evolve_map[name_cur_state]:
                #one step ahead
                des_each_possible_state = des[each_possible_state]
                if(des_each_possible_state < 1.0):
                    self.oop1()
                else:
                    self.oop2()



        oop1_list = self.Opp_1_2()
    #    oop2_list = self.Opp2()
    #    oop3_list = self.Opp3()



        opp = {}

    def action_applicable(name_cur_state, evolve_map, action):
        next_action = evolve_map[name_cur_state]

        for each_next in next_action:
            if (action == each_action[0]):
                return each_action[1]

        return None

    ##from test file

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
                    list_oop.append(Opportunity('oop0', action, cur_state, each_level, oop0_alpha))
                else:
                    oop1_alpha = oop_1(des, list_bnf)
                    list_oop.append(Opportunity('oop1', action, cur_state, each_level, oop1_alpha))

                    oop2_alpha = oop_2(des, list_bnf)
                    list_oop.append(Opportunity('oop2', action, cur_state, each_level, oop2_alpha))

                    oop3_alpha = oop_3(future_states)
                    list_oop.append(Opportunity('oop3', action, cur_state, each_level, oop3_alpha))

                    oop4_alpha = oop_4(future_states)
                    list_oop.append(Opportunity('oop4', action, cur_state, each_level, oop4_alpha))

                    des_latest_states = return_desirability_list(states, state_des)
                    oop5_alpha = oop_5(des_latest_states, list_bnf)
                    list_oop.append(Opportunity('oop5', action, cur_state, each_level, oop5_alpha))

                    oop6_alpha = oop_6(des_latest_states, list_bnf)
                    list_oop.append(Opportunity('oop6', action, cur_state, each_level, oop6_alpha))

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
