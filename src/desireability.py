import copy
class CalculateDesireability():
    def __init__(self):
        self.map_of_desirability = {}
        self.desirable_situation = {}

        self.original_desirability_values = {}

    def add_situation(self, situ, rule, value):
        """
            To set desirability of each situation
        """
        self.map_of_desirability[situ] = {
            'rule' : rule,
            'value' : value
            }

    def update_desirability_Function(intent_list, value):
        #past values deleted when new intention assigned
        self.desirable_situation = {}
        for each_intent in intent_list:
            self.desirable_situation[intent] = {
                'rule' : intent_list[each_intent],
                'value' : value
            }

    def desirabilityFunction(self, map_of_states, hashmap):
        desirability = {}

        for key in hashmap:
            desirability[key] = {}
            state = hashmap[key]
            res = self.isStateDesiable(state)
            desirability[key] = {
                #'state' : state,
                'value' : res
            }

        return desirability


    def isStateDesiable(self, state):
        """
            If state is desirable for all rules, then state is undesirable == FALSE,
            otherwise state is desirable == TRUE

            It is a fuzzy (probabilistic) description of desirability. State desirability
            decreases according to desireability of undesreable situations.
        """

        status = []
        for key in self.map_of_desirability:
            insight = self.isDesirable(state, self.map_of_desirability[key]['rule'])

            #No levelisation on desirability function, but we could check that shoul we want half desirability like considered as fatal or not
            if (insight):
                calculated_res = 1.0 #Desirable State
            else:
                calculated_res = self.map_of_desirability[key]['value'] #which is value that set by user 0 for fatal, and 0.5 for half desire,
            status.append(calculated_res)

        for key in self.desirable_situation:
            high_light = self.isIntended(state, self.desirable_situation[intent]['rule'])
            if (insight):
                calculated_res = 1.0 #Intented State
            else:
                calculated_res = self.desirable_situation[intent]['value'] #which is value that set by user 0 for fatal, and 0.5 for half desire,
            status.append(calculated_res)

        def multiplyList(myList) :
            # Multiply elements one by one
            result = 1
            for x in myList:
                result = result * x
            return result

        return multiplyList(status)


    def isDesirable(self, state, rule):
        """
            Check all elements of rule is in the state description
            If all elements found in state, then state is undesirable == FALSE,
            otherwise state is desirable == TRUE
        """
        return not(all([x in state for x in rule]))

    def isIntended(self, state, rule):

        return any([x in state for x in rule])
