from src.planner import run_planning

import time
import math

class Intention():

    def __init__(self):
        self.plan_map = {}
        self.history_of_intention = {} #according to time
        #self.history_of_desirability = {}

    def create_recogniser(self, list_of_goals, domain, problem):
    #Create map of all plan and goal

        for e in list_of_goals:
            plan = run_planning(domain, problem[e])
            self.plan_map[e] = plan

        intent_list = self.intention_selection(self.plan_map)
        return intent_list

    def return_map(self):
        return self.plan_map

    def intention_selection(self, maped):
        '''
            Function for predict user intention
            It depends on cost (length) of the plan and compare all other plans to decide stortest plan
            Shortest plan represents the intention of user
            Ref:
        '''
        #set if there is no plan to inf and length of plan
        maped_temp = {}
        for k in maped:
            if (len(maped[k]) == 0):
                maped_temp[k] = math.inf
            else:
                maped_temp[k] = len(maped[k])

        #find minimum value of in whole list
        minval = min(maped_temp.values())

        #return list of intended goal
        intent_list = [k for k in maped_temp if maped_temp[k] == minval]

        #Added intetntion list to the list of history_of_intention according to time
        self.history_of_intention[time.time()] = intent_list.copy()
        intent_map = {}
        for i in intent_list:
            intent_map[i] = []
            for list_element in maped[i]:
                temp = "(" + list_element  + ")"
                intent_map[i].append(temp)

        return intent_list, intent_map, minval

    # def return_desirability_value(self):
    #     els = list(self.history_of_desirability)
    #     return self.history_of_desirability[els[-1]]
    #
    # def desirability_detection(self, intent_list, len_list_goal):
    #     '''
    #         Function of desirability detection;
    #         It depends on frequent was intended action on the plan_list
    #     '''
    #     map_desireable = {}
    #
    #     #chose the last one
    #
    #
    #     #update value according to frequency of appear
    #     for item in intent_list:
    #         values = self.bayesian_probability(item, len(intent_list),len_list_goal)
    #         map_desireable[item] = values
    #
    #     map = self.normalise_value(map_desireable)
    #
    #     self.history_of_desirability[time.time()] = map
    #     return map
    #
    # def normalise_value(self, maped_temp):
    #     total_count = 0
    #
    #     for each in maped_temp:
    #         total_count += maped_temp[each]
    #
    #     for each in maped_temp:
    #         maped_temp[each] = maped_temp[each] / total_count
    #
    #     return maped_temp
    #
    # def bayesian_probability(self, intended_action, len_intended_action, len_list_goal):
    #
    #     count = 0
    #     length = 0
    #     for e in self.history_of_intention:
    #         length += 1
    #         if intended_action in self.history_of_intention[e]:
    #             count += 1
    #
    #
    #     frequency_occurance = count / length
    #     current_prob = 1 / len_intended_action
    #     general_prob = 1 / len_list_goal
    #
    #     value = (frequency_occurance + current_prob) / general_prob
    #     return value
