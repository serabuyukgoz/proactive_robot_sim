from src.string_modification import *
from src.desireability import CalculateDesireability
from src.opportunity import OpportunityDetection

import copy

class Equilibrium_Maintenance():
    def __init__(self, system):
        self.des = CalculateDesireability()
        self.oop = OpportunityDetection(system)

        self.name_state_hash_map = {}
        self.map_of_states = {} #free_run adjacency list

    ## Function related to defining environment ##

    # Set evolve_map by hand and set it to system
    def set_env(self, map_state, hashmap):
        self.name_state_hash_map = copy.deepcopy(hashmap)
        self.map_of_states = copy.deepcopy(map_state)

    def return_state_hash_map(self):
        return copy.deepcopy(self.name_state_hash_map)

    def return_evolve_map(self):
        return copy.deepcopy(self.map_of_states)

    # Probabilistic way to create evolve_map for definite K
    def create_evolve_map_define_by_K(self, current_state, action_list, K):
        #Function to check if state placed in hash map already
        name_state = self.add_naming(current_state)
        undone_state = {0 : [{'name' : name_state, 'state_array' : current_state}] }
        #undone_state.append(current_state)
        for i in range(K+1):
            undone_state[i+1] = []
            while(undone_state[i]):
                state = undone_state[i].pop()
                name_state = state['name']
                current_state = state['state_array']
                for action in action_list:
                    #new_state = self.add_action_to_state_plan(current_state, action_list[action], action_list)
                    new_state = self.add_action_to_state(current_state, action_list[action])
                    if (len(new_state) > 0):
                        name = self.return_name_of_state(new_state)
                        if (name):
                            #self.map_of_states[name_state].append([action, name])
                            if (name not in self.map_of_states[name_state]):
                                self.map_of_states[name_state].append(name)
                        else:
                            new_name = self.add_naming(new_state)
                            #self.map_of_states[name_state].append([action, new_name])
                            self.map_of_states[name_state].append(new_name)
                            #self.create_evolve_map_define_by_K(new_state, action_list)
                            undone_state[i+1].append({ 'name' :  new_name, 'state_array' : new_state})

        return copy.deepcopy(self.map_of_states)

    # Probabilistic way to create evolve_map for all possibilities
    def create_evolve_map(self, current_state, action_list):
        #Function to check if state placed in hash map already
        name_state = self.add_naming(current_state)
        undone_state = {0 : [{'name' : name_state, 'state_array' : current_state}] }
        #undone_state.append(current_state)
        for i in range(K+1):
            undone_state[i+1] = []
            while(undone_state[i]):
                state = undone_state[i].pop()
                name_state = state['name']
                current_state = state['state_array']
                for action in action_list:
                    #new_state = self.add_action_to_state_plan(current_state, action_list[action], action_list)
                    new_state = self.add_action_to_state(current_state, action_list[action])
                    if (len(new_state) > 0):
                        name = self.return_name_of_state(new_state)
                        if (name):
                            #self.map_of_states[name_state].append([action, name])
                            if (name not in self.map_of_states[name_state]):
                                self.map_of_states[name_state].append(name)
                        else:
                            new_name = self.add_naming(new_state)
                            #self.map_of_states[name_state].append([action, new_name])
                            self.map_of_states[name_state].append(new_name)
                            #self.create_evolve_map_define_by_K(new_state, action_list)
                            undone_state[i+1].append({ 'name' :  new_name, 'state_array' : new_state})

        return copy.deepcopy(self.map_of_states)


    def add_naming(self, state):
        #function for adding state to the hashmap and evoluation map

        #first check if the state already exist
        name = self.return_name_of_state(state)
        if (name):
            name_state = name
        else:
            #No : Set name to a state
            if (len(state) > 0):
                name_state = ';'.join(state)
            else:
                name_state = '(Empty)'
                self.name_state_hash_map[name_state] = state

        # this is to define new sloths
        if (name_state not in self.map_of_states):
            self.map_of_states[name_state] = []

        return name_state

    def add_action_to_state_name(self, state_name, action):

        #search state describtion from name
        state = self.return_state_from_name(state_name)
        if (state):
            new_state = self.add_action_to_state(state, action)
            new_state_name = self.return_name_of_state(new_state)

            return new_state_name, new_state
        else:
            raise Exception("ERR: State name is not found in hashmap, cannot add action to state")

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

    def return_name_of_state(self, key):
        for i in self.name_state_hash_map:
            k = self.name_state_hash_map[i]
            if (len(key) == len(k)):
                if (all([x in k for x in key])):
                    return i
        return None

    def return_state_from_name(self, name):
        if name in self.name_state_hash_map:
            return copy.deepcopy(self.name_state_hash_map[name])
        return None
