import os
import tempfile
import time
from collections import OrderedDict
import copy
import re

class ActionType():
    def __init__(self, types, parameter, precondition, effect, name):
        self.types = types
        self.parameter = parameter
        self.precondition = precondition
        self.effect = effect
        self.name = name

class Environment():
    def __init__(self):

        self.action_dictionary = {}
        self.human_action_dictionary = {}
        self.robot_action_dictionary = {}

        self.goals_dictionary = {}
        self.objects_dictionary = {}
        self.types_dictionary = {}

        self.predicates_list = []
        self.derived_list = []

        self.common_knowledge_dictionary = [] #which represents the general knowledge
        self.init_state = [] #which represents the current state

        self.history_of_state_change = {}
        self.history_of_state_evolution = {}
        self.state_evolve_map_history = OrderedDict()

    def add_action(self, types, parameter, precondition, effect, name):
        action_name = name + "_action"
        self.action_dictionary[action_name] = ActionType(types, parameter, precondition, effect, name)

    def add_predicate(self, predicate):
        self.predicates_list.append(predicate)
        #Later it could be more dynamic to extracted from the other definitions

    def add_goal(self, name):
        #create goal objects
        if self.goals_dictionary.get(name) == None:
            self.goals_dictionary[name] = []

    def add_sub_goal(self, goal, sub_goal):
        #adding sub goals to goal objects
        self.goals_dictionary[goal].append(sub_goal)

    def add_type(self, name):
        if self.types_dictionary.get(name) == None:
            self.types_dictionary[name] = []

    def add_sub_types(self, types, sub_type):
        self.types_dictionary[types].append(sub_type)

    def add_object(self, name):
        #to check if obejct already decleared before
        if self.objects_dictionary.get(name) == None:
            self.objects_dictionary[name] = []

    def add_sub_objects(self, name, objects):
        self.objects_dictionary[name].append(objects)

    def add_common_knowledge(self, info):
        #add informan=tion onto the list
        self.common_knowledge_dictionary.append(info)

    def add_derived(self, info):
        self.derived_list.append(info)

    def findNegate(self, strs):
        if ("(not(" in strs):
            strs = strs.replace("(not(", "(")
            strs = strs.replace("))", ")")
            return strs
        else:
            return 0

    def add_state_change(self, state_change):
        #Instead of incrementing negates delete them from state description
        neg = self.findNegate(state_change)
        if (neg):
            self.init_state.remove(neg)
        else:
            self.init_state.append(state_change)

        #add change into the history
        self.history_of_state_change[time.time()] = self.return_current_state()

    def return_predicates(self):
        return copy.deepcopy(self.predicates_list)#.deepCopy()

    def return_action_list(self):
        #returning all actions at the dictionary
        return copy.deepcopy(self.action_dictionary)

    def provide_action_list(self):
        action_list = self.return_action_list()
        listed_action = {}

        for key in action_list:
            if action_list[key].types == "Robot":
                #print(key, "->" ,self.action_dictionary[key])
                listed_action[key] = action_list[key]

        return copy.deepcopy(listed_action)

    def return_robot_action_list(self):
        action_list = self.return_action_list()
        listed_action = {}

        for key in action_list:
            if action_list[key].types == "Robot":
                #print(key, "->" ,self.action_dictionary[key])
                #listed_action.append(action_list[key])
                listed_action[key] = action_list[key]
        return copy.deepcopy(listed_action)

    def return_human_action_list(self):
        action_list = self.return_action_list()
        listed_action = {}

        for key in action_list:
            if action_list[key].types == "Human":
                #print(key, "->" ,self.action_dictionary[key])
                listed_action[key] = action_list[key]

        return copy.deepcopy(listed_action)

    def return_state_action_list(self):
        action_list = self.return_action_list()
        listed_action = {}

        for key in action_list:
            if action_list[key].types == "Free":
                #print(key, "->" ,self.action_dictionary[key])
                listed_action[key] = action_list[key]

        return copy.deepcopy(listed_action)

    def return_objects_list(self):
        return copy.deepcopy(self.objects_dictionary)

    def return_goal_list(self):
        lists = []
        for i in self.goals_dictionary.keys():
            lists.append(i)

        return copy.deepcopy(lists)

    def return_current_knowledge_list(self):
        # self.common_knowledge_dictionary.append(" has_a cake water " )
        return copy.deepcopy(self.common_knowledge_dictionary)

    def return_current_state(self):
        return copy.deepcopy(self.init_state)

    def return_types(self):
        return copy.deepcopy(self.types_dictionary)

    def return_derived_list(self):
        return copy.deepcopy(self.derived_list)

    def create_environment(self):
        types_list = self.return_types()
        predicates_list = self.return_predicates()
        #action_list = self.return_action_list()
        action_list = self.return_human_action_list()

        objects =  self.return_objects_list()
        relationship_list = self.return_current_knowledge_list()
        list_init = self.return_current_state()
        goal_list = self.return_goal_list()

        derived_list = self.return_derived_list()

        domain_name = self.create_domain(types_list, predicates_list, action_list, derived_list)
        problem_name = {}
        for g in goal_list:
            problem_name[g] = self.create_problem(g, objects, relationship_list, list_init)


        #Retruned PDDL Files as whole; domain and all goals
        return (domain_name, problem_name)


    def create_domain(self, types_list, predicates_list, action_list, derived_list):
        name_domain = "domain.pddl"

        f = open(name_domain, "w+")

        f.write(" (define (domain recipe) \n" +
              "(:requirements \n" +
              " :strips \n" +
              " :negative-preconditions \n" +
              " :equality \n" +
              " :typing \n" +
              " :derived-predicates ) \n")


        f.write(" (:types ")

        for items in types_list:
            for item in types_list[items]:
                f.write(item)
                f.write(" ")

            if (len(types_list[items]) > 0):
                f.write(" - ")
            f.write(items)
            f.write(" \n ")

        f.write(
        " ) \n (:predicates ")

        for items in predicates_list:
            f.write(" (")
            f.write(items)
            f.write(") \n ")

        f.write(")")
        for der in derived_list:
            f.write(der)

        for each in action_list:
            each_action = action_list[each]
            f.write(
                "  (:action " + each_action.name + "\n "+
                "    :parameters" + each_action.parameter + "\n "+
                "    :precondition "+ each_action.precondition +  " \n "+
                "    :effect " + each_action.effect + " \n "+
                "  ) \n ")

        #final paranthesis
        f.write(
        " ) \n ")

        f.close()

        return name_domain

    def create_problem(self, goal, objects, relationship_list, list_init):
        names = re.sub('[()]', '', goal)
        names = names.replace(" ", "_")
        name_problem = "problem_%s.pddl" %names

        f= open(name_problem,"w+")

        f.write("(define (problem recipe-ex1) \n" +
        "  (:domain recipe) \n" +
        "  (:objects  \n" )

        for obj in objects:
            for item in objects[obj]:
                f.write(" %s - %s \n" %(item, obj))

        f.write(
        " \n ) \n (:init   \n" )

        for items in relationship_list:
            f.write(" (")
            f.write(items)
            f.write(") \n ")

        #write init
        for event in list_init:
          f.write(" %s  \n" %event)

        f.write( ")(:goal \n" ) #adding goal

        #add goal
        f.write("%s" %goal)
        f.write (" ) ) ") #last paranthesis

        f.close()

        return name_problem

    def return_state_evolution(self):
        els = list(self.state_evolve_map_history)
        return copy.deepcopy(self.state_evolve_map_history[els[-1]])

    def evolve_state_free_run(self, plan_list, time_stamp):
        #TO-DO
        #add the model of state evolvation through the time such as food distord and etc.
        #Not sure how to model state evolvation of and how to link with time stamp
        evolve_state = {}
        evolve_state["t_0"] = {'current' : self.return_current_state() }
        for tim in range(time_stamp):
            key = "t_" + str(tim+1)
            one_time = {}
            for intent in plan_list:
                #calculate intent
                pp = self.calculate_state(plan_list[intent] ,tim+1)
                one_time[intent] = copy.deepcopy(pp)

            evolve_state[key] = copy.deepcopy(one_time)

        self.state_evolve_map_history[time.time()] = copy.deepcopy(evolve_state)
        return copy.deepcopy(evolve_state)

    def evolve_state(self, intent_list, plan_list, time_stamp):

        #free run or intention depend on if there is an intention;
        if not intent_list:
            map_state = self.evolve_state_free_run(plan_list, time_stamp)
            return copy.deepcopy(map_state)

        evolve_state = {}
        evolve_state["t_0"] = {'current' : self.return_current_state() }
        for tim in range(time_stamp):
            key = "t_" + str(tim+1)
            one_time = {}
            for intent in intent_list:
                #calculate intent
                pp = self.calculate_state(plan_list[intent] ,tim+1)

                #to check if there is a plan
                if pp:
                    one_time[intent] = copy.deepcopy(pp)

            #to check if there is a plan or not
            if one_time:
                evolve_state[key] = copy.deepcopy(one_time)

        self.state_evolve_map_history[time.time()] = copy.deepcopy(evolve_state)
        return evolve_state

    def calculate_state(self, plan, leng):
        #to prevent index out of boundary
        if leng > len(plan):
            return []

        evolved_plan = self.return_current_state()
        for index in range(leng):
            i = plan[index]
            key = i.split(" ") #to get predicate

            act = key[0] + "_action"
            pair = self.action_dictionary[act].effect
            result = pair.split(" ")

            strs = result[0]
            for s in range(len(result)-1):
                strs += " " + key[s+1]
            strs += ")"

            neg = self.findNegate(strs)
            if (neg):
                evolved_plan.remove(neg)
            else:
                evolved_plan.append(strs)

        return copy.deepcopy(evolved_plan)

    def add_action_to_state(self, state, action):

        # parameters and variables

        def return_parameter(param):
            param = param.replace("(", "")
            param = param.replace(")", "")
            param = param.replace(" -", "")
            pp = param.split(" ")
            print(pp)
            parameter = {}

            for all in pp:
                parameter[pp.pop()] = pp.pop()
            return parameter

        list_parameter = return_parameter(action.parameter)

        for x in list_parameter:
            key = list_parameter[x]
            list_parameter[x] = copy.deepcopy(self.objects_dictionary[list_parameter[x]])


        # precondition satisfied
        def list_of_precondition(precon):
            pp = []
            if ("(and" in precon):
                precon = precon.replace("(and", "")
                precon = precon.replace("))", ")")
                precon = precon.replace(") (", ");(")
                pp = precon.split(";")
            else:
                pp.append(precon)
            return pp


        # add effect

        next_state = []
        print(action.precondition)
        print(action.effect)
        print("Next State -> ")
        print(next_state)




        return copy.deepcopy(next_state)
