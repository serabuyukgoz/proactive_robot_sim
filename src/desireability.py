import copy
class CalculateDesireability():
    def __init__(self):
        self.map_of_undesirable_situations = {}
        self.desirable_situation = {}

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

    def stateDesirabilityValue(self, state, repeat_map):
        """
            If state is desirable for all rules, then state is undesirable == FALSE,
            otherwise state is desirable == TRUE

            It is a fuzzy (probabilistic) description of desirability. State desirability
            decreases according to desireability of undesreable situations.
        """

        # if state is empty, then there is no desirability, Which is 0
        if (state == []):
            return 0

        status = []
        #set desirability values
        for key in self.map_of_undesirable_situations:
            insight = self.isDesirable(state, self.map_of_undesirable_situations[key]['rule'])

            # #No levelisation on desirability function, but we could check that shoul we want half desirability like considered as fatal or not
            # if (insight):
            #     #insight = 1
            #     calculated_res = 1.0 #Desirable State
            # else:
            #     #insight = 0
            #     calculated_res = self.map_of_undesirable_situations[key]['value'] #which is value that set by user 0 for fatal, and 0.5 for half desire,

            calculated_res = int(insight) + ((1 - int(insight))*(self.map_of_undesirable_situations[key]['value']+(repeat_map[key]/100)))
            status.append(calculated_res)

        for key in self.desirable_situation:
            degree = self.degree_of_intetion_on_state(state, self.desirable_situation[key]['rule'])
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
        return multiplyList(status)

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

    def undesirableRepetation(self, cur_state, des_map):

        for each_elem in self.map_of_undesirable_situations:
            res = self.isDesirable(cur_state, self.map_of_undesirable_situations[each_elem]['rule'])
            if (res == False):
                des_map[each_elem] = des_map[each_elem] + 1

        return copy.deepcopy(des_map)
