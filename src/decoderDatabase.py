

class ActionType():
    def __init__(self, types, parameter, precondition, effect):
        self.types = types
        self.parameter = parameter
        self.precondition = precondition
        self.effect = effect


class DecodeDatabase():
    """This class is for read from database and create ontology of
    planner for human actions. It also stores all actions, objects and predicates
    in a dictionary of each"""

    def __init__(self):
        self.action_dictionary = {} #stores all Human and Robot actions
        self.action_dictionary_nested = {} #it is the differnet techinic to use of dictionary to use it
        self.predicate_dictionary = {} #stores all predicates
        self.objects_dictionary = {}
        self.goals_dictionary = {} #it listed all goals could be achieved, and maybe sub goals as an items related to each goal
        self.init_dictionary = {} #Current state description by time
        self.state_description = [] #list of current states

    def add_action(self):
        #This class normally read from database and etract actions but for now it is only add actions
        self.action_dictionary["tell_action"] = ActionType("Robot", "", "", "")
        self.action_dictionary["pick_action"] = ActionType("Human", "", "", "")
        self.action_dictionary["place_action"] = ActionType("Human", "", "", "")

        # TODO ---? How to change robot action to satisfy user's plan
        tell_action = {
            "types" : "Robot",
            "parameter" : "",
            "precondition" : "",
            "effect" : "",
            "name" : "tell_action"
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


        self.action_dictionary_nested[tell_action['name']] = tell_action
        self.action_dictionary_nested[collect_action['name']] = collect_action
        self.action_dictionary_nested[leave_action['name']] = leave_action
        self.action_dictionary_nested[submit_action['name']] = submit_action

    def add_goal_list(self):
        '''This function is to extract all goals and (maybe) related sub-goals to listed '''

        self.goals_dictionary["soup"] = ""
        self.goals_dictionary["cake"] = ""

    def add_init_state(self, state_change):

        self.state_description.append(state_change)

    def return_action_list(self):
        """ This function seperated action which robot can do to use later"""

        listed_action = []
        list_as_object = []

        #Two different way to exlude robot actions
        for key in self.action_dictionary:
            if self.action_dictionary[key].types == "Robot":
                #print(key, "->" ,self.action_dictionary[key])
                list_as_object.append(self.action_dictionary[key])

        for key in self.action_dictionary_nested:
            if self.action_dictionary_nested[key]["types"] == "Human":
                #print(key, "->" ,self.action_dictionary_nested[key])
                listed_action.append(self.action_dictionary_nested[key])

        return listed_action

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
        return 0

    def evolving_state(self, plan):
        evolved_plan = []
        for i in plan:
            key = i.split(" ")
            print (key)
            pair = self.action_dictionary_nested[key[0]]['effect']
            print (pair)
            result = pair.split(" ")
            print(result)

            strs = result[0]
            for s in range(len(result)-1):
                strs += " " + key[s+1]
            strs += ")"

            evolved_plan.append(strs)

            print("Resulted String -> %s " %strs)

        return evolved_plan

if __name__ == "__main__":

    print("Hello World!")
    dd = DecodeDatabase()
    dd.add_goal_list()
    lists = dd.return_goal_list()
    for i in lists:
        print (i)
    print(lists[0])
