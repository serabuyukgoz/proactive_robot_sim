import copy
class CalculateDesireability():
    def __init__(self):
        self.map_of_undesirable_situations = {}
        self.desirable_situation = {}
        self.des_map = {}
        self.des_map_flag = False

    def add_des_map(self, map):
        self.des_map = map
        self.des_map_flag = True

    def add_situation(self, situ, rule, value):
        """
            To set desirability of each situation
        """
        self.map_of_undesirable_situations[situ] = {
            'rule' : rule,
            'value' : value
            }

    def update_desirability_Function(self, intent_list, set_value):
        #past values deleted when new intention assigned
        self.desirable_situation = {}
        for each_intent in intent_list:
            self.desirable_situation[each_intent] = {
                'rule' : intent_list[each_intent],
                'value' : set_value
            }
        return copy.deepcopy(self.desirable_situation)


    def stateDesirabilityValueActionApplied(self, state_obj, alpha_state_obj):

        if (state_obj.desirability == -1):
            state_des = self.stateDesirabilityValue(state_obj)

        if (alpha_state_obj.desirability == -1):
            alpha_state_des = self.stateDesirabilityValue(alpha_state_obj)

        print("Des alpha(x) CHECK -> \n \t State: {} \n {} \n \t State a applied: {} \n {}  ".format(state_obj.desirability, state_obj.name, alpha_state_obj.desirability, alpha_state_obj.name))

        if (state_obj.desirability == alpha_state_obj.desirability):
            #BNF, applied alpha has no effect
            print("Des alpha(x) CHECK: 0")
            return 0
        #
        # if (alpha_state_obj.desirability > state_obj.desirability):
        #     #BNF, applied alpha has positive effect
        #     print("Des alpha(x) CHECK: {}".format(alpha_state_obj.desirability - state_obj.desirability))
        #     return alpha_state_obj.desirability - state_obj.desirability

        elif (alpha_state_obj.desirability == -1):
            print("Des alpha(x) CHECK: 0")
            return 0 #no state to apply

        else:
            #BNF, applied alpha has negative effect
            print("Des alpha(x) CHECK: {}".format(alpha_state_obj.desirability))
            return alpha_state_obj.desirability




    def stateDesirabilityValue(self, state_obj):
        """
            If state is desirable for all rules, then state is undesirable == FALSE,
            otherwise state is desirable == TRUE

            It is a fuzzy (probabilistic) description of desirability. State desirability
            decreases according to desireability of undesreable situations.
        """

        if(self.des_map_flag):
            print('IN DES MAP')
            # print("Des Value of {} = {}".format(state_obj.name, self.des_map[state_obj.name]))
            if (state_obj.name in self.des_map):
                return self.des_map[state_obj.name]
            else:
                return 0

        else:
            # if state is empty, then there is no desirability, Which is 0
            if (state_obj.state == []):
                return 0

            # if (state_obj.desirability != -1):
            #     return state_obj.desirability

            status = []
            #set desirability values
            for key in self.map_of_undesirable_situations:
                insight = self.isDesirable(state_obj.state, self.map_of_undesirable_situations[key]['rule'])

                calculated_res = int(insight) + ((1 - int(insight))*(self.map_of_undesirable_situations[key]['value']))
                status.append(calculated_res)

            for key in self.desirable_situation:
                degree = self.degree_of_intetion_on_state(state_obj.state, self.desirable_situation[key]['rule'])
                calculated_res = degree * self.desirable_situation[key]['value']
                if (degree == 0):
                    calculated_res = 1.0 #to prevent the make the desirable state undesirable
                # high_light = self.isIntended(state, self.desirable_situation[key]['rule'])
                # if (high_light):
                #     calculated_res = 1.0 #Intented State
                # else:
                #     calculated_res = self.desirable_situation[key]['value'] #which is value that set by user 0 for fatal, and 0.5 for half desire,
                status.append(calculated_res)

            def multiplyList(myList) :
                # Multiply elements one by one
                result = 1
                for x in myList:
                    result = result * x
                return result

            #print("DES: State {} \n Desirability : {}".format(state, multiplyList(status)))
            des = multiplyList(status)
            state_obj.setStateDesirability(des)
            return des

    def degree_of_intetion_on_state(self, state, list_intent):
        """
            It calculates the degree of found in state
            If there is only 1 element in state, the undesirability ratio will be higher
            In this way, we could jump to the
        """

        value = 0

        for each_element in list_intent:
            if (each_element in state):
                value += 1

        value = value / len(list_intent)
        value = (1 - value)
        return value

    def isDesirable(self, state, rule):
        """
            Check all elements of rule is in the state description
            If all elements found in state, then state is undesirable == FALSE,
            otherwise state is desirable == TRUE
        """
        return not(all([x in state for x in rule]))

    def isIntended(self, state, rule):
        return any([x in state for x in rule])

    def cut_off_branches(self, evolve_map, hashmap_state, intention_map, action_list, cur_state_name):

        list_intention = []
        for each_intention in intention_map:
            for action in intention_map[each_intention]:
                act = action_list[action]
                list_intention = list_intention + act['effect']

        print(evolve_map[cur_state_name])
        for each_branch in evolve_map[cur_state_name]:
            #check is linked with intention rule?
            delta = self.isIntended(hashmap_state[each_branch], list_intention)
            if (delta != True):
                print(delta)
                print(len(evolve_map[cur_state_name]))
                evolve_map[cur_state_name].remove(each_branch)
                print(len(evolve_map[cur_state_name]))
        return copy.deepcopy(evolve_map)


    def setUndesirabilityMap(self):
        map  = {}

        for each_elem in self.map_of_undesirable_situations:
            map[each_elem] = 0

        return copy.deepcopy(map)
