from src.string_modification import *
from src.desireability import CalculateDesireability
from src.opportunity import OpportunityDetection

import copy

class Situation():
    def __init__(self, pre, eff):
        self.precondition = pre
        self.effect = eff

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
        # for each_state in hashmap:
        #     self.name_state_hash_map[each_state] = StateDefinition(each_state, hashmap[each_state], -1)
        self.name_state_hash_map = hashmap
        self.map_of_states = map_state
        # for each_state in map_state:
        #     self.map_of_states[each_state] = []
        #     for each_name in map_state[each_state]:
        #         state = self.return_state_object_from_name(each_name)
        #         self.map_of_states[each_state].append(state)

        return self.map_of_states, self.name_state_hash_map

    def set_hashmap(self, hashmap, desmap):
        for each_state in hashmap:
            obj = self.return_object_of_state(hashmap[each_state])
            obj.setStateDesirability(desmap[each_state])

    def return_state_hash_map(self):
        # return copy.deepcopy(self.name_state_hash_map)
        return self.name_state_hash_map

    def return_evolve_map(self):
        # return copy.deepcopy(self.map_of_states)
        return self.map_of_states

    def findTemp(self, current_state):

        if('(temp 0)' in current_state):
            return 1
        if('(temp 1)' in current_state):
            return 2
        if('(temp 2)' in current_state):
            return 3
        if('(temp 3)' in current_state):
            return 4
        if('(temp 4)' in current_state):
            return 5

    def create_state(self, key_list, hashmap):

        def find_name(key):
            for i in hashmap:
                k = hashmap[i]
                if (len(key) == len(k.state)):
                    if (all([x in k.state for x in key])):
                        print(k.state)
                        return i, k
            return None, None

        name, k = find_name(key_list)
        if (name):
            return k, name, hashmap
        else:
            name = ';'.join(key_list)
            ss = StateDefinition(name, key_list, -1)
            hashmap[name] = ss
            return ss, name, hashmap

    def add_situation_to_state(self, state, rule):
        # add effect
        new_state = []
        new_state = copy.deepcopy(state)

        wanted_precon, unwanted_precon = seperate_not_predicate(rule.precondition)
        # if all precondition is in and also consider not :( if there is not then if not part is not belong to list
        satisfied_wanted = all([x in state for x in wanted_precon])
        satisfied_unwanted = all([elem not in state for elem in unwanted_precon])
        if (satisfied_wanted and satisfied_unwanted):
            #add effect to the state and return state
            w, u = seperate_not_predicate(rule.effect)
            new_state = new_state + w #add to element
            new_state = [i for i in new_state if i not in u] #remove the elements which named as not

        return copy.deepcopy(new_state)


    def fuction_F_k(self, free_map, current_state):
        maps = {}
        hash_map = self.name_state_hash_map
        undone_state = []


        state_def, name, hash_map = self.create_state(current_state, hash_map)
        maps[name] = []
        undone_state.append(state_def)

        while(undone_state):
            state_obj = undone_state.pop()

            level = self.findTemp(state_obj.state)
            # print("LEVEL:{}".format(level))

            #creating a sloth for new defined state
            if (state_obj.name not in maps):
                maps[state_obj.name] = []
            # Go through each action to be probable
            # print("STATE NAME: {}".format(state_obj.name))
            if (level in free_map):
                for each_temp in free_map[level]:
                    state_transform = state_obj.state
                    # print('STATE START: {}'.format(state_transform))
                    for each_rule in each_temp:
                        state_transform = self.add_situation_to_state(state_transform, each_rule)
                        # print('STATE TRANSFORM: {}'.format(state_transform))


                    state_def, name, hash_map = self.create_state(state_transform, hash_map)
                    # to prevent repetation in the look-up table
                    if (name not in maps[state_obj.name]):
                        maps[state_obj.name].append(state_def)
                        undone_state.append(state_def)

            # print("MAPS: {}".format(maps))

        set_map, set_hashmap = self.set_env(maps, hash_map)
        return copy.deepcopy(set_map)


    # Probabilistic way to create evolve_map
    def create_evolve_map_define(self, current_state, action_list):
        maps = {}
        hash_map = self.name_state_hash_map
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

        wanted_precon, unwanted_precon = seperate_not_predicate(action.precondition)
        # if all precondition is in and also consider not :( if there is not then if not part is not belong to list
        satisfied_wanted = all([x in state for x in wanted_precon])
        satisfied_unwanted = all([elem not in state for elem in unwanted_precon])
        if (satisfied_wanted and satisfied_unwanted):
            #add effect to the state and return state
            w, u = seperate_not_predicate(action.effect)
            new_state = copy.deepcopy(state)
            new_state = new_state + w #add to element
            new_state = [i for i in new_state if i not in u] #remove the elements which named as not

        return copy.deepcopy(new_state)

    def check_precondition(self, state, action):

        wanted_precon, unwanted_precon = seperate_not_predicate(action.precondition)
        # if all precondition is in and also consider not :( if there is not then if not part is not belong to list
        satisfied_wanted = all([x in state for x in wanted_precon])
        satisfied_unwanted = all([elem not in state for elem in unwanted_precon])

        return (satisfied_wanted and satisfied_unwanted)

    def add_action(self, state, action):
        new_state = []

        #add effect to the state and return state
        w, u = seperate_not_predicate(action.effect)
        new_state = copy.deepcopy(state)
        new_state = new_state + w #add to element
        new_state = [i for i in new_state if i not in u] #remove the elements whic

        return copy.deepcopy(new_state)

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
