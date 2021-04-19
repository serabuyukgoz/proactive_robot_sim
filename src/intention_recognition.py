from src.planner import run_planning

import time

class Intention():

    def __init__(self):
        self.plan_map = {}
        self.history_of_intention = {} #according to time

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

        return intent_list

    def desirability_detection(self):
        '''
            Function of desirability detection;
            It depends on frequent was intended action on the plan_list
        '''

        map_desireable = {}

        #sort list

        #chose the last one

        #update value according to frequency of appear


        return map_desireable
