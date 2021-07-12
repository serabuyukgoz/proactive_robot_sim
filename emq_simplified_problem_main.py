import os
import tempfile
import subprocess
import copy

import time

from src.environment import Environment
from src.planner import run_planning
from src.intention_recognition import Intention
from src.desireability import CalculateDesireability
from src.opportunity import OpportunityDetection

from src.naive_proactivity import Naive

from print_strategy import print_all, print_des, print_evolve_map
from extract_graph import graph

# My game start from here
system = { }

def setClasses():
    env = Environment(system)
    rec = Intention()
    des = CalculateDesireability()
    opo = OpportunityDetection(system)

    system["env"] = env
    system["recogniser"] = rec
    system["des"] = des
    system["opo"] = opo

    nav = Naive()
    system["nav"] = nav


def create_world_state(system):

    system['env'].add_type('main')
    system['env'].add_sub_types('main', 'obj')
    system['env'].add_sub_types('main', 'agent')
    system['env'].add_sub_types('main', 'weather')
    system['env'].add_sub_types('main', 'time')

    #adding agent's action for intention recognition

    system['env'].add_action("Human", "(?u - agent)", "(not(outside ?u))", "(outside ?u)", "leave_home")
    system['env'].add_action("Human", " ( ) ", "(dishes_dirty)", "(not(dishes_dirty))", "clean_dishes")
    # system['env'].add_action("Human", "(?u - agent)", "(and (collected backpack) (collected compass) (outside ?u))", "(hiking ?u)", "go_hiking")
    # system['env'].add_action("Human", "(?u - agent)", "(and (collected walking_stick) (collected dog) (outside ?u))", "(promenade ?u)", "go_promenade")
    # system['env'].add_action("Human", "(?u - agent)", "(and (not (outside ?u)) )", "(watching_tv ?u)", "watch_tv")
    # system['env'].add_action("Human", "(?u - agent)", "(and (not (outside ?u)) (collected book))", "(reading_book ?u)", "read_book")
    system['env'].add_action("Human", "(?x - obj)", "(not(collected ?x))", "(collected ?x)", "collect")
    system['env'].add_action("Human", "(?x - obj)", "(collected ?x)", "(not(collected ?x))", "leave")
    #added robot actions for equilibrium maintenance, all of robot's action is communicative

    system['env'].add_action("Robot", "( )", "(dishes_dirty)", "(not(dishes_dirty))", "tell_clean_dishes")
    system['env'].add_action("Robot", "(?x - obj)", "(not(collected ?x))", "(collected ?x)", "tell_gather")
    system['env'].add_action("Robot", "(?u - agent)", "(current_weather hail)", "(not(outside ?u))", "warn_hail")
#    system['env'].add_action("Robot", "( )", "(current_weather rain)", "(collected umbrella)", "warn_rain")

    #added actions for free run, changes of concepts!
    system['env'].add_action("Free", "(?wp - weather ?wn - weather)", "(current_weather ?wp)", "(and (not (current_weather ?wp)) (current_weather ?wn))", "weather_change")
    system['env'].add_action("Free", "(?tp - time ?tn - time)", "(after ?tp ?tn)", "(and (not (current_time ?tp)) (current_time ?tn))", "time_change")
    system['env'].add_action("Free", "(?u - agent)", "(breakfast ?u)", "(and  (not (breakfast ?u)) (dishes_dirty))", "had_breakfast")

    system['env'].add_predicate("collected ?x - objects")
    system['env'].add_predicate("outside ?u - agent")
    system['env'].add_predicate("current_weather ?w - weather")
    system['env'].add_predicate("current_time ?t - time")
    system['env'].add_predicate("after ?t1 - time ?t2 - time")

    # system['env'].add_predicate("hiking ?u - agent")
    # system['env'].add_predicate("promenade ?u - agent")
    # system['env'].add_predicate("watching_tv ?u - agent")
    # system['env'].add_predicate("reading_book ?u - agent")
    system['env'].add_predicate("breakfast ?u - agent")

    system['env'].add_predicate("weather_dealt")
    system['env'].add_predicate("dishes_dirty")

    # system['env'].add_goal('( hiking ?u - agent)')
    # system['env'].add_goal('( promenade ?u - agent)')
    # system['env'].add_goal('( reading_book ?u - agent)')
    # system['env'].add_goal('( watching_tv ?u - agent)')

    #hiking
    system['env'].add_goal('(and (collected backpack) (collected compass) (collected water_bottle) (outside user))')
    #promenade
    system['env'].add_goal('(and (collected walking_stick) (collected dog) (collected water_bottle) (outside user))')
    # #watching_tv
    # system['env'].add_goal('(and (not (outside user)) )')
    #reading_book
    # system['env'].add_goal('(and (not (outside user)) (collected backpack) (collected book))')

    system['env'].add_object('agent')
    system['env'].add_sub_objects('agent', 'user')

    system['env'].add_constants('weather')
    system['env'].add_sub_constants('weather', 'sunshine')
    system['env'].add_sub_constants('weather', 'hail')
    system['env'].add_sub_constants('weather', 'rainy')
    system['env'].add_sub_constants('weather', 'cloudy')
    system['env'].add_constants('time')
    system['env'].add_sub_constants('time', 'morning')
    system['env'].add_sub_constants('time', 'noon')
    system['env'].add_sub_constants('time', 'evening')
    system['env'].add_constants('obj')
    system['env'].add_sub_constants('obj', 'hat')
    system['env'].add_sub_constants('obj', 'compass')
    system['env'].add_sub_constants('obj', 'backpack')
    system['env'].add_sub_constants('obj', 'walking_stick')
    system['env'].add_sub_constants('obj', 'dog')
    system['env'].add_sub_constants('obj', 'book')
    system['env'].add_sub_constants('obj', 'water_bottle')
    system['env'].add_sub_constants('obj', 'umbrella')

    #relationship added
    system['env'].add_common_knowledge(" after morning lunch " )
    system['env'].add_common_knowledge(" after lunch after_noon " )
    system['env'].add_common_knowledge(" after after_noon evening " )
    system['env'].add_common_knowledge(" after evening night " )
    system['env'].add_common_knowledge(" after night morning " )

    #related to the state description -> it could have chage later
    system['env'].add_state_change("(current_weather sunshine)")
    system['env'].add_state_change("(current_time morning)")
    system['env'].add_state_change("(breakfast user)")

    #ALSO add what is undesired situations to define which state will be undesired!
    system['des'].add_situation('get_wet', ['(current_weather rainy)' , '(outside ?u - agent)'], 0.7)
    system['des'].add_situation('get_hurt', ['(current_weather hail)' , '(outside ?u - agent)'], 1.0)
    system['des'].add_situation('dirt_dishes', ['(dishes_dirty)'], 0.4)

    domain_name, problem_name = system['env'].create_environment()

    return (domain_name, problem_name)


def updateSituation(system):
    domain_name, problem_name = system['env'].create_environment()
    list_of_goals = system['env'].return_goal_list()

    '''
        HiR
        Result of intention recognition
        - intent = List of intent
        - intent_map = Map of intent and plan to reach
        - dynamic_k = length of plan
    '''
    intent, intent_map, dynamic_k = system['recogniser'].create_recogniser(list_of_goals, domain_name, problem_name)


    act_robot = system['env'].return_robot_action_list()
    unvoluntary_action_list = system['env'].return_unvoluntary_action_list()
    cur_state_name, cur_state = system['env'].return_current_state()

    defined_action = system['env'].create_action_list_map(unvoluntary_action_list)


    '''
        EQM

        First create evolve_map - hypothetical map to forecast future
    '''
    react = time.time()
    evolve_map = system['emq'].create_evolve_map(cur_state, defined_action)
    react = time.time() - react

    hashmap_state = system['emq'].return_state_hash_map()

    #Define intention recogniton as opportunity
    i = 0.2 #desirability value


    ########################
    # 1)
    #Change K
    K = 2 #look up strategy
    #K = dynamic_k
    #K = 0
    ########################

    #############################
    # 2)
    #cut off brances
    evolve_map = system['emq'].des.cut_off_branches(evolve_map, hashmap_state, intent_map, defined_action, cur_state_name, K)

    #limitate with K
    #evolve_map = system['des'].limitate(evolve_map, hashmap_state, cur_state_name, dynamic_k)
    print_evolve_map(evolve_map)
    ###############################

    #######################################
    # 3 ) Changes desireability function
    des = system['emq'].des.desirabilityFunction(evolve_map, hashmap_state)
    print('______________________')
    print('Desirabilily Calculation \n {}'.format(des))

    #Change Desirability Value
    #system['des'].update_desirability_Function(intent_map, i)

    # des = system['des'].desirabilityFunction(evolve_map, hashmap_state)
    # print('______________________')
    # print('Desirabilily Calculation Modifed Intention\n {}'.format(des))
    #############################################

    #####
    # 4)
    #
    #turn HiR actions into opportunity to match with EqM's oppotunities


    oop_intent = system['emq'].oop.set_as_oop(intent_map, cur_state_name, cur_state, des, defined_action, i)
    ###########


    opp_eqm = system['emq'].opp.findOpportunity(evolve_map, des, cur_state_name, act_robot, K)

    return opp_eqm, oop_intent, evolve_map, react


if __name__ =='__main__':
    print("Hello World!")
    setClasses()

    domain_name, problem_name = create_world_state(system)
    #for every change in Situation
    react = time.time()
    opp_emq, opp_hir, state_evolvation, reaction_time = updateSituation(system)
    react = time.time() - react


    map = system['env'].return_state_map()
    print_evolve_map(map)
    print('Length = {}'.format(len(map)))
    print('Final Map --------')
    print_evolve_map(state_evolvation)
    print_all(react, opp_emq, opp_hir, system)

    print('Final Map Length = {}'.format(len(state_evolvation)))
    print("Calculation Time -> {}".format(reaction_time))
    graph(state_evolvation)
