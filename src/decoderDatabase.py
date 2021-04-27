import time
from collections import OrderedDict

class ActionType():
    def __init__(self, types, parameter, precondition, effect, name):
        self.types = types
        self.parameter = parameter
        self.precondition = precondition
        self.effect = effect
        self.name = name


class DecodeDatabase():
    """This class is for read from database and create ontology of
    planner for human actions. It also stores all actions, objects and predicates
    in a dictionary of each"""

    def __init__(self):
        self.action_dictionary = {} #stores all Human and Robot actions
        self.action_dictionary_nested = {} #it is the differnet techinic to use of dictionary to use it
        self.predicate_dictionary = {} #stores all predicates
        self.predicate_list = []
        self.relationship_list = []
        self.objects_dictionary = {}
        self.goals_dictionary = {} #it listed all goals could be achieved, and maybe sub goals as an items related to each goal
        self.init_dictionary = {} #Current state description by time
        self.state_description = [] #list of current states
        self.types_dictionary = {}
        self.state_map_history = {}
        self.state_evolve_map_history = OrderedDict()

    #def define_action(self, precondition, predicate, effect):

    def add_predicate(self, predicate, parameter):

        #deliminate string with the inner paranthesis

        #the deliminate strign with
        return 0

    def add_action(self):
        #This class normally read from database and etract actions but for now it is only add actions
        self.action_dictionary["tell_submit_action"] = ActionType("Robot", "(?d - dish)", "(collected_all ?d)", "(submitted ?d)", "submit")
        self.action_dictionary["tell_pick_action"] = ActionType("Robot", "(?x - food)", "(not(collected ?x))", "(collected ?x)", "collect")
        self.action_dictionary["tell_leave_action"] = ActionType("Robot", "(?x - food)", "(collected ?x)", "(not(collected ?x))", "leave")

        self.add_predicate("(collected_all ?d)", "(?d - dish)")
        self.add_predicate("(submitted ?d)", "(?d - dish)")
        self.add_predicate("(collected ?x)", "(?x - food)")
        self.add_predicate("(not(collected ?x))", "(?x - food)")
        # TODO ---? How to change robot action to satisfy user's plan
        tell_collect_action = {
            "types" : "Robot",
            "parameter" : "(?x - food)",
            "precondition" : "(not(collected ?x))",
            "effect" : "(collected ?x)",
            "name" : "collect"
        }

        tell_leave_action = {
            "types" : "Robot",
            "parameter" : "(?x - food)",
            "precondition" : "(collected ?x)",
            "effect" : "(not(collected ?x))",
            "name" : "leave"
        }

        tell_submit_action = {
            "types" : "Robot",
            "parameter" : "(?d - dish)",
            "precondition" : "(collected_all ?d)",
            "effect" : "(submitted ?d)",
            "name" : "submit"
        }

        # TODO ---? How to remove paranthesis from the definition
        collect_action = {
            "types" : "Human",
            "parameter" : "(?x - food)",
            "precondition" : "(not(collected ?x))",
            "effect" : "(collected ?x)",
            "name" : "collect"
        }

        leave_action = {
            "types" : "Human",
            "parameter" : "(?x - food)",
            "precondition" : "(collected ?x)",
            "effect" : "(not(collected ?x))",
            "name" : "leave"
        }

        submit_action = {
            "types" : "Human",
            "parameter" : "(?d - dish)",
            "precondition" : "(collected_all ?d)",
            "effect" : "(submitted ?d)",
            "name" : "submit"
        }

        self.action_dictionary_nested[collect_action['name']] = collect_action
        self.action_dictionary_nested[leave_action['name']] = leave_action
        self.action_dictionary_nested[submit_action['name']] = submit_action
        self.action_dictionary_nested[tell_collect_action['name']] = tell_collect_action
        self.action_dictionary_nested[tell_leave_action['name']] = tell_leave_action
        self.action_dictionary_nested[tell_submit_action['name']] = tell_submit_action

    def add_goal_list(self):
        '''This function is to extract all goals and (maybe) related sub-goals to listed '''

        self.goals_dictionary["soup"] = ""
        self.goals_dictionary["cake"] = ""

    def add_init_state(self, state_change):
        self.state_description.append(state_change)

    def return_types(self):
        self.types_dictionary["main"] = ['dish', 'food']
        return self.types_dictionary

    def return_predicates(self):
        self.predicate_list.append("collected_all ?d - dish")
        self.predicate_list.append("submitted ?d - dish")
        self.predicate_list.append("collected ?x - food")
        self.predicate_list.append("has_a ?s - dish ?x - food")
        return self.predicate_list

    def return_actions(self):
        return self.action_dictionary

    def return_action_list(self):
        """ This function seperated action which robot can do to use later"""

        listed_action = {}
        list_as_object = []

        #Two different way to exlude robot actions
        # for key in self.action_dictionary:
        #     if self.action_dictionary[key].types == "Robot":
        #         #print(key, "->" ,self.action_dictionary[key])
        #         list_as_object.append(self.action_dictionary[key])

        for key in self.action_dictionary_nested:
            if self.action_dictionary_nested[key]["types"] == "Robot":
                #print(key, "->" ,self.action_dictionary_nested[key])
                listed_action[key] = self.action_dictionary_nested[key]

        return listed_action

    def return_objects_list(self):
        self.objects_dictionary["dish"] = ["soup", "cake"]
        self.objects_dictionary['food'] = ['water', 'flour', 'lentil', 'chocolate', 'sugar', 'salt', 'pepper']

        return self.objects_dictionary

    def return_relationship_list(self):
        self.relationship_list.append(" has_a soup water " )
        self.relationship_list.append(" has_a soup salt " )
        self.relationship_list.append(" has_a soup pepper " )
        self.relationship_list.append(" has_a soup lentil " )
        self.relationship_list.append(" has_a cake flour " )
        self.relationship_list.append(" has_a cake chocolate " )
        self.relationship_list.append(" has_a cake sugar " )
        self.relationship_list.append(" has_a cake water " )

        return self.relationship_list

    def return_goal_list(self):
        lists = []
        for i in self.goals_dictionary.keys():
            lists.append(i)

        return lists

    def return_current_state(self):
        """ This fuction is to show current state of the human  """
        return self.state_description

    def return_evolving_state(self):
        """ This fuction is to show the estimated future states of the human  """
        els = list(self.state_evolve_map_history)
        return self.state_evolve_map_history[els[-1]]

    def generate_evolving_state(self, intent_list, plan_list):

        state_map = {}
        for i in intent_list:
            evolve = self.evolving_state(plan_list[i])
            state_map[i] = evolve

        self.state_evolve_map_history[time.time()] = state_map

        return state_map


    def evolving_state(self, plan):
        evolved_plan = []
        for i in plan:
            key = i.split(" ")
        #    print (key)
            pair = self.action_dictionary_nested[key[0]]['effect']
        #    print (pair)
            result = pair.split(" ")
        #    print(result)

            strs = result[0]
            for s in range(len(result)-1):
                strs += " " + key[s+1]
            strs += ")"

            evolved_plan.append(strs)

        #    print("Resulted String -> %s " %strs)

        return evolved_plan

if __name__ == "__main__":

    print("Hello World!")
    dd = DecodeDatabase()
    dd.add_goal_list()
    lists = dd.return_goal_list()
    for i in lists:
        print (i)
    print(lists[0])
