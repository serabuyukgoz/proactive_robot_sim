
class CalculateDesireability():
    def __init__(self):
        self.map_of_desirability = {}

    def add_situation(self, situ, rule, value):
        """
            To set desirability of each situation
        """
        self.map_of_desirability[situ] = {
            'rule' : rule,
            'value' : value
            }

    def desirabilityFunction(self, state_zero, map_of_states):
        desirability = {}
        for sub_set in map_of_states:
            for key in map_of_states[sub_set]:
                res = self.isStateDesiable(map_of_states[sub_set][key])
                naming = str(sub_set) + "_" + str(key)
                desirability[naming] = {
                    'state' : map_of_states[sub_set][key],
                    'value' : res
                }
        return desirability


    def isStateDesiable(self, state):
        """
            If state is desirable for all rules, then state is undesirable == FALSE,
            otherwise state is desirable == TRUE
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
