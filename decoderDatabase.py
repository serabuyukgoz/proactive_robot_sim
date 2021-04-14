

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
        self.action_dictionary_nested = {} #stores all objects
        self.predicate_dictionary = {} #stores all predicates


    def add_action(self):
        #This class normally read from database and etract actions but for now it is only add actions
        self.action_dictionary["tell_action"] = ActionType("Robot", "", "", "")
        self.action_dictionary["pick_action"] = ActionType("Human", "", "", "")
        self.action_dictionary["place_action"] = ActionType("Human", "", "", "")

        tell_action = {
            "types" : "Robot",
            "parameter" : "",
            "precondition" : "",
            "effect" : "",
            "name" : "tell_action"
        }

        pick_action = {
            "types" : "Human",
            "parameter" : "",
            "precondition" : "",
            "effect" : "",
            "name" : "pick_action"
        }

        place_action = {
            "types" : "Human",
            "parameter" : "",
            "precondition" : "",
            "effect" : "",
            "name" : "place_action"
        }

        self.action_dictionary_nested["tell_action"] = tell_action
        self.action_dictionary_nested["pick_action"] = pick_action
        self.action_dictionary_nested["place_action"] = place_action

    def return_action_list(self):
        """ This function seperated action which robot can do to use later"""

        listed_action = []
        list_as_object = []
        for key in self.action_dictionary:
            if self.action_dictionary[key].types == "Robot":
                #print(key, "->" ,self.action_dictionary[key])
                list_as_object.append(self.action_dictionary[key])

        for key in self.action_dictionary_nested:
            if self.action_dictionary_nested[key]["types"] == "Human":
                #print(key, "->" ,self.action_dictionary_nested[key])
                listed_action.append(self.action_dictionary_nested[key])


        return listed_action

if __name__ == "__main__":

    print("Hello World!")
    dd = DecodeDatabase()
    print(dd.action_dictionary)
    dd.add_action()
    print(dd.action_dictionary)
    print(dd.action_dictionary_nested)

    print(dd.action_dictionary["tell_action"].types)
    print(dd.action_dictionary_nested["tell_action"]["types"])

    act = dd.return_action_list()
    print(act)
