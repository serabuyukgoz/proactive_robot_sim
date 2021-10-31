from src.string_modification import *
from src.desireability import CalculateDesireability
from src.opportunity import OpportunityDetection

import copy

class StateDefinition():
    def __init__(self, name, state, des):
        self.name = name
        self.state = state
        self.desirability = des

    def setStateDescription(self, state_des):
        self.state = state_des

    def setStateDesirability(self, des):
        self.desirability = des

    def setStataName(self, name):
        self.name = name

class Equilibrium_Maintenance():
    def __init__(self, system):
        self.des = CalculateDesireability()
        self.oop = OpportunityDetection(system)

        self.name_state_hash_map = {}
        self.map_of_states = {} #free_run adjacency list
        #
    ## Function related to defining environment ##

    # Set evolve_map by hand and set it to system
    def set_env(self, map_state, hashmap):
        #For each state in hashmap turn into a state object - TO DO
        for each_state in hashmap:
            self.name_state_hash_map[each_state] = StateDefinition(each_state, hashmap[each_state], -1)

        for each_state in map_state:
            self.map_of_states[each_state] = []
            for each_name in map_state[each_state]:
                state = self.return_state_object_from_name(each_name)
                self.map_of_states[each_state].append(state)

        return self.map_of_states, self.name_state_hash_map

    def return_state_hash_map(self):
        # return copy.deepcopy(self.name_state_hash_map)
        return self.name_state_hash_map

    def return_evolve_map(self):
        # return copy.deepcopy(self.map_of_states)
        return self.map_of_states

    # Probabilistic way to create evolve_map
    def create_evolve_map_define(self, current_state, action_list):
        maps = {}
        hash_map = {}
        undone_state = []

        name, hash_map = self.create_naming(current_state, hash_map)
        maps[name] = []
        undone_state.append(name)

        while(undone_state):
            state_name = undone_state.pop()
            #creating a sloth for new defined state
            if (state_name not in maps):
                maps[state_name] = []
            # Go through each action to be probable
            for each_act in action_list:
                new_state = self.add_action_to_state(current_state, action_list[each_act])
                # Empty state means action is not applicable to state
                if (new_state != []):
                    name, hash_map = self.create_naming(new_state, hash_map)
                    # to prevent repetation in the look-up table
                    if (name not in maps[state_name]):
                        maps[state_name].append(name)
                        undone_state.append(name)

        set_map, set_hashmap = self.set_env(maps, hash_map)
        return copy.deepcopy(set_map)

    def create_naming(self, key_list, hashmap):

        def find_name(key):
            for i in hashmap:
                k = hashmap[i]
                if (len(key) == len(k)):
                    if (all([x in k for x in key])):
                        return i
            return None

        name = find_name(key_list)
        if (name):
            return name, hashmap
        else:
            name = ';'.join(key_list)
            hashmap[name] = key_list
            return name, hashmap

    def add_action_to_state(self, state, action):
        # add effect
        new_state = []

        wanted_precon, unwanted_precon = seperate_not_predicate(action['precondition'])
        # if all precondition is in and also consider not :( if there is not then if not part is not belong to list
        satisfied_wanted = all([x in state for x in wanted_precon])
        satisfied_unwanted = all([elem not in state for elem in unwanted_precon])
        if (satisfied_wanted and satisfied_unwanted):
            #add effect to the state and return state
            w, u = seperate_not_predicate(action['effect'])
            new_state = copy.deepcopy(state)
            new_state = new_state + w #add to element
            new_state = [i for i in new_state if i not in u] #remove the elements which named as not

        return copy.deepcopy(new_state)

    def check_precondition(self, state, action):

        wanted_precon, unwanted_precon = seperate_not_predicate(action['precondition'])
        # if all precondition is in and also consider not :( if there is not then if not part is not belong to list
        satisfied_wanted = all([x in state for x in wanted_precon])
        satisfied_unwanted = all([elem not in state for elem in unwanted_precon])

        return (satisfied_wanted and satisfied_unwanted)

    def add_action(self, state, action):
        new_state = []

        #add effect to the state and return state
        w, u = seperate_not_predicate(action['effect'])
        new_state = copy.deepcopy(state)
        new_state = new_state + w #add to element
        new_state = [i for i in new_state if i not in u] #remove the elements whic

        return copy.deepcopy(new_state)


    # def add_action_now_effect_later(self, cur_state, future_state, action):
    #     # add effect
    #     new_state = []
    #
    #     wanted_precon, unwanted_precon = seperate_not_predicate(action['precondition'])
    #     # if all precondition is in and also consider not :( if there is not then if not part is not belong to list
    #     satisfied_wanted = all([x in cur_state for x in wanted_precon])
    #     satisfied_unwanted = all([elem not in cur_state for elem in unwanted_precon])
    #     if (satisfied_wanted and satisfied_unwanted):
    #         #add effect to the state and return state
    #         w, u = seperate_not_predicate(action['effect'])
    #         new_state = copy.deepcopy(future_state)
    #         new_state = new_state + w #add to element
    #         new_state = [i for i in new_state if i not in u] #remove the elements which named as not
    #
    #     return copy.deepcopy(new_state)


    def return_state_object_from_name(self, name):
        for i in self.name_state_hash_map:
         if (name == self.name_state_hash_map[i].name):
            return self.name_state_hash_map[i]
        return None

    def return_object_of_state(self, key):
        for i in self.name_state_hash_map:
            k = self.name_state_hash_map[i]
            if (len(key) == len(k.state)):
                if (all([x in k.state for x in key])):
                    return k

        if (key == []):
            return StateDefinition(None, [], -1)

        name = ';'.join(key)
        state_obj = StateDefinition(name, key, -1)
        self.name_state_hash_map[name] = state_obj
        return state_obj
