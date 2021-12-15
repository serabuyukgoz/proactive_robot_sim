import copy
class CalculateDesireability():
    def __init__(self):
        self.map_of_undesirable_situations = {}
        self.desirable_situation = {}
        self.des_map_flag = False

    def add_des_map(self, map):
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

    def stateDesirabilityValue(self, state_obj):

        # If state is empty, then there is no desirability, Which is 0
        if (state_obj.state == []):
            return 0

        if (state_obj.desirability != -1):
            return state_obj.desirability

        if (self.des_map_flag):
            return 0

        des = self.desirabilityFunction(state_obj.state)

        state_obj.setStateDesirability(des)
        return des

    def desirabilityFunction(self, state):

        """
            If state is desirable for all rules, then state is undesirable == FALSE,
            otherwise state is desirable == TRUE

            It is a fuzzy (probabilistic) description of desirability. State desirability
            decreases according to desireability of undesreable situations.
        """

        status = []
        state_map = copy.deepcopy(state)
        #set desirability values
        for key in self.map_of_undesirable_situations:
            insight = self.isDesirable(state, self.map_of_undesirable_situations[key]['rule'])

            calculated_res = int(insight) + ((1 - int(insight))*(self.map_of_undesirable_situations[key]['value']))

            if (calculated_res != 1):
                state_map = [x for x in state_map if x not in self.map_of_undesirable_situations[key]['rule']]

            status.append(calculated_res)

        def multiplyList(myList) :
            # Multiply elements one by one
            result = 1
            for x in myList:
                result = result * x
            return result

        #print("DES: State {} \n Desirability : {}".format(state, multiplyList(status)))
        des = multiplyList(status)
        des = des / len(state_map)
        print("Underability {}, : {}".format(state_map, des))
        return des

    def isDesirable(self, state, rule):
        """
            Check all elements of rule is in the state description
            If all elements found in state, then state is undesirable == FALSE,
            otherwise state is desirable == TRUE
        """
        return not(all([x in state for x in rule]))
