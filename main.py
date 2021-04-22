import os
import tempfile
import subprocess
import copy

import time


from src.decoderDatabase import DecodeDatabase
from src.create_domain_problem_file import create_domain, create_problem
from src.planner import run_planning
from src.intention_recognition import Intention

import json #just for better printing

# My game start from here
system = { }

def updateSituation(system):
    #create domain
    ask_action = system['listener'].return_actions()
    domain_file = create_domain(ask_action)
    list_of_goals = system['listener'].return_goal_list()
    init = system['listener'].return_current_state()

    #create plan file for all goals
    problem_file = {}
    for e in list_of_goals:
        problem_file[e] = create_problem(e, init)

    #intent + plan
    intent = system['recogniser'].create_recogniser(list_of_goals, domain_file, problem_file)

    desire = system['recogniser'].desirability_detection(intent, len(list_of_goals))

    plan_list = system['recogniser'].return_map()
    evolve_map = system['listener'].generate_evolving_state(intent, plan_list)


def print_all(react, system):
    print("-----------------------------------------------")
    print("Reaction time in millisec %s" %react )
    print("--- For Equilibrium Maintenance ----")
    #return desirability Function
    print("Desirability Function -> %s " %(system['recogniser'].return_desirability_value()))
    #return current state
    separator = '  \n '
    print("Current State -> \n %s" %(separator.join(system['listener'].return_current_state())))
    #return state evolvation
    print("State Evolvation -> ")
    print_dict(system['listener'].return_evolving_state())
    #return action list
    act_list = system['listener'].return_action_list()
    print("Action List ->")
    print_act(act_list)

    print("-----------------------------------------------")

def print_dict(dct):
    separator = ' \n '
    for item, amount in dct.items():
        print(" -- {} : \n {}".format(item, separator.join(amount)))

def print_act(dct):
    for item, amount in dct.items():
        print(" ** {}".format(item))
        for i, a in amount.items():
            print(" \t {} : {}".format(i, a))

def setClasses():
    lis = DecodeDatabase()
    rec = Intention()
    #ass = Perception(system)

    system["listener"] = lis
    system["recogniser"] = rec
#    system["assistance"] = ass

if __name__ =='__main__':

    print("Hello World!")
    setClasses()
    #dd = DecodeDatabase()
    #print(dd.action_dictionary)
    system['listener'].add_action()
    system['listener'].add_goal_list()
    print("Initial setup done!")


    #for every change in Situation
    react = time.time()
    updateSituation(system)
    react = time.time() - react

    print_all(react, system)

    #Situation change
    print("action played -> collected pepper")
    system['listener'].add_init_state("collected pepper")

    react = time.time()
    updateSituation(system)
    react = time.time() - react

    print_all(react, system)

    #Situation change
    print("action played -> collected chocolate")
    system['listener'].add_init_state("collected chocolate")

    react = time.time()
    updateSituation(system)
    react = time.time() - react

    print_all(react, system)
