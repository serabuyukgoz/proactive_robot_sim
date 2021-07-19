import os
import tempfile
import time
from collections import OrderedDict
import copy
import re
from src.string_modification import *


class ActionType():
    def __init__(self, types, parameter, precondition, effect, name):
        self.types = types
        self.parameter = parameter
        self.precondition = precondition
        self.effect = effect
        self.name = name

class Environment():
    def __init__(self, system):

        self.domain_name = ""
        self.sys = system

        self.action_dictionary = {} #all actions store there
        self.human_action_dictionary = {}
        self.robot_action_dictionary = {}

        self.goals_dictionary = {}
        self.objects_dictionary = {}
        self.types_dictionary = {}
        self.constant_dictionary = {}

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

    def add_constants(self, name):
        #to check if obejct already decleared before
        if self.constant_dictionary.get(name) == None:
            self.constant_dictionary[name] = []

    def add_sub_constants(self, name, objects):
        self.constant_dictionary[name].append(objects)

    def add_common_knowledge(self, info):
        #add informan=tion onto the list
        self.common_knowledge_dictionary.append(info)

    def add_derived(self, info):
        self.derived_list.append(info)

    #Till here it was all about creating PDDL file

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

    def return_unvoluntary_action_list(self):
        action_list = self.return_action_list()
        listed_action = {}

        for key in action_list:
            if action_list[key].types != "Robot":
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

        mapped_action = self.create_action_list_map(listed_action)
        return copy.deepcopy(mapped_action)

    def return_human_action_list(self):
        action_list = self.return_action_list()
        listed_action = {}

        for key in action_list:
            if action_list[key].types == "Human":
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

    def return_constants_list(self):
        return copy.deepcopy(self.constant_dictionary)

    def return_derived_list(self):
        return copy.deepcopy(self.derived_list)

    def create_environment(self):
        types_list = self.return_types()
        predicates_list = self.return_predicates()
        #action_list = self.return_action_list()
        action_list = self.return_human_action_list()

        objects =  self.return_objects_list()
        constants_list = self.return_constants_list()
        relationship_list = self.return_current_knowledge_list()
        list_init = self.return_current_state()
        goal_list = self.return_goal_list()

        derived_list = self.return_derived_list()
        domain_name = self.create_domain(types_list, constants_list, predicates_list, action_list, derived_list)
        problem_name = {}
        for g in goal_list:
            problem_name[g] = self.create_problem(g, objects, relationship_list, list_init)

        '''
            After environment created
            Specifiy action_list could be done
            Create the environment state graph from the initial state that robot in
        '''

        # defined_action = self.create_action_list_map()
        # self.create_evolve_map(list_init, defined_action)

        #Retruned PDDL Files as whole; domain and all goals
        self.domain_name = domain_name
        return (domain_name, problem_name)


    def create_domain(self, types_list, constants_list, predicates_list, action_list, derived_list):
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


        f.write( " ) \n (:constants \n ")

        for items in constants_list:
            for item in constants_list[items]:
                f.write(item)
                f.write(" ")

            if (len(constants_list[items]) > 0):
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
          f.write(event)
          f.write(" \n ")

        f.write( ")(:goal \n" ) #adding goal

        #add goal
        f.write("%s" %goal)
        f.write ("  ) ) ") #last paranthesis

        f.close()

        return name_problem

    def create_action_list_map(self, action_list):

        listed_action = {}

        for key in action_list:
            #print(key, "->" ,action_list[key])
            action = action_list[key]
            #action part
            list_parameter = return_parameter(action.parameter)
            map_parameters = {**self.constant_dictionary, **self.objects_dictionary} #merge two dictionary

            for x in list_parameter:
                key = list_parameter[x]
                list_parameter[x] = map_parameters[list_parameter[x]]

            ll_precon = list_of_precondition(action.precondition)
            ll_effect = list_of_precondition(action.effect)

            ll_parameters = specify_parameters(list_parameter)

            for each_parameter in ll_parameters:
                #check scenario for each parameter
                lists = [each_parameter[x] for x in each_parameter]
                parameter = ' '.join(lists)
                name_of_action = '(' + action.name + ' ' + parameter + ')'
                #print('======== {} ======'.format(name_of_action))
                #but first turn update precondition
                each_precon = turn_precondition(each_parameter, ll_precon)
                each_effect = turn_precondition(each_parameter, ll_effect)
                listed_action[name_of_action] = {
                    'name' : name_of_action,
                    'precondition' : each_precon,
                    'effect' : each_effect
                }

        return copy.deepcopy(listed_action)


    def add_naming(self, state):
        #function for adding state to the hashmap and evoluation map
        if (len(state) > 0):
            name_state = ';'.join(state)
        else:
            name_state = '(Empty)'
        self.name_state_hash_map[name_state] = state

        if (name_state not in self.map_of_states):
            self.map_of_states[name_state] = []

        return name_state
