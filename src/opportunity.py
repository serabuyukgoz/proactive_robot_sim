
class Opportunity():
    def __init__(self, current_state, action, next_state, current_des, next_des):
        self.s_p = current_state
        self.s_n = next_state
        self.a = action

        #Those are to calculate how the played action changed opportunity
        self.des_p = current_des
        self.des_n = next_des
        self.delta = next_des - current_des

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
