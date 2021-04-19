import os
import tempfile
import subprocess
import copy

import time


from src.decoderDatabase import DecodeDatabase
from src.create_domain_problem_file import create_domain, create_problem
from src.planner import run_planning
from src.intention_recognition import Intention

# My game start from here
system = { }


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


    #for every change in Situation
    react = time.time()
    #create domain
    domain_file = create_domain()
    list_of_goals = system['listener'].return_goal_list()
    init = system['listener'].return_current_state()

    #create plan file for all goals
    problem_file = { }
    plan_list = {}
    evolve_plan = {}
    for e in list_of_goals:
        problem_file[e] = create_problem(e, init)
        plan_list[e] = run_planning(domain_file, problem_file[e])
        print(plan_list[e])
        evolve = system['listener'].evolving_state(plan_list[e])
        print(evolve)
        evolve_plan[e] = evolve


    #intent + plan
    intent = system['recogniser'].create_recogniser(list_of_goals, domain_file, problem_file)
    print(intent)
    react = time.time() - react
    print("Reaction time in millisec %s" %react )
    print(system['recogniser'].return_map())

    print("--- For Equilibrium Maintenance ----")
    #return desirability Function
    print("Desirability Function -> %s " %(system['recogniser'].desirability_detection()))
    #return current state
    print("Current State -> %s" %(system['listener'].return_current_state()))
    #return state evolvation
    print("State Evolvation -> %s" %evolve_plan) #%(system['listener'].return_evolving_state()))
    #return action list
    print("Action List -> %s " %(system['listener'].return_action_list()))
    print("-----------------")

    #Situation change
    system['listener'].add_init_state("collected pepper")
    react = time.time()
    init = system['listener'].return_current_state()
    #plan for all goals
    for e in list_of_goals:
        problem_file[e] = create_problem(e, init)
        plan_list[e] = run_planning(domain_file, problem_file[e])
        print("%s , %s " %(e, plan_list[e]))

    #intent + plan
    intent = system['recogniser'].create_recogniser(list_of_goals, domain_file, problem_file)
    print(intent)
    react = time.time() - react
    print("Reaction time in millisec %s" %react )
    print(system['recogniser'].return_map())

    print("--- For Equilibrium Maintenance ----")
    #return desirability Function
    print("Desirability Function -> %s " %(system['recogniser'].desirability_detection()))
    #return current state
    print("Current State -> %s" %(system['listener'].return_current_state()))
    #return state evolvation
    print("State Evolvation -> %s" %(system['listener'].return_evolving_state()))
    #return action list
    print("Action List -> %s " %(system['listener'].return_action_list()))
    print("-----------------")
