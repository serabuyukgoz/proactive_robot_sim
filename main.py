import os
import tempfile
import subprocess
import copy
import sys

import time

from src.environment import Environment
from src.planner import Planner
from src.intention_recognition import Intention
from src.desireability import CalculateDesireability
from src.opportunity import OpportunityDetection
from src.equilibrium_maintenance import Equilibrium_Maintenance

from src.naive_proactivity import Naive

from print_strategy import *
from extract_graph import graph

# My game start from here
system = { }

def setClasses():
    env = Environment(system)
    pla = Planner()
    rec = Intention(pla)
    emq = Equilibrium_Maintenance(system)


    system["env"] = env
    system["recogniser"] = rec
    system["emq"] = emq
    system['pla'] = pla

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
    system['env'].add_action("Human", "(?u - agent)", "(and (dishes_dirty) (not(outside ?u)) )", "(not(dishes_dirty))", "clean_dishes")
    # system['env'].add_action("Human", "(?u - agent)", "(and (collected backpack) (collected compass) (outside ?u))", "(hiking ?u)", "go_hiking")
    # system['env'].add_action("Human", "(?u - agent)", "(and (collected walking_stick) (collected dog) (outside ?u))", "(promenade ?u)", "go_promenade")
    # system['env'].add_action("Human", "(?u - agent)", "(and (not (outside ?u)) )", "(watching_tv ?u)", "watch_tv")
    # system['env'].add_action("Human", "(?u - agent)", "(and (not (outside ?u)) (collected book))", "(reading_book ?u)", "read_book")
    system['env'].add_action("Human", "(?u - agent ?x - obj)", "(and (not(collected ?u ?x)) (not(outside ?u)) )", "(collected ?u ?x)", "collect")
    # system['env'].add_action("Human", "(?u - agent ?x - obj)", "(and (collected ?u ?x) (not(outside ?u)) )", "(not(collected ?u ?x))", "leave")
    #added robot actions for equilibrium maintenance, all of robot's action is communicative

    system['env'].add_action("Robot", "(?u - agent)", "(and (dishes_dirty) (not(outside ?u)) )", "(not(dishes_dirty))", "tell_clean_dishes")
    system['env'].add_action("Robot", "(?u - agent ?x - obj)", "(not(collected ?u ?x))", "(collected ?u ?x)", "tell_gather")
    system['env'].add_action("Robot", "(?u - agent)", "(current_weather hail)", "(not(outside ?u))", "warn_hail")
#    system['env'].add_action("Robot", "( )", "(current_weather rain)", "(collected umbrella)", "warn_rain")

    #added actions for free run, changes of concepts!
    system['env'].add_action("Free", "(?wp - weather ?wn - weather)", "(current_weather ?wp)", "(and (not (current_weather ?wp)) (current_weather ?wn))", "weather_change")
    # system['env'].add_action("Free", "(?tp - time ?tn - time)", "(after ?tp ?tn)", "(and (not (current_time ?tp)) (current_time ?tn))", "time_change")
    system['env'].add_action("Free", "(?u - agent)", "(breakfast ?u)", "(and  (not (breakfast ?u)) (dishes_dirty))", "had_breakfast")

    system['env'].add_predicate("collected ?u - agent ?x - objects")
    system['env'].add_predicate("outside ?u - agent")
    system['env'].add_predicate("current_weather ?w - weather")
    # system['env'].add_predicate("current_time ?t - time")
    # system['env'].add_predicate("after ?t1 - time ?t2 - time")
    system['env'].add_predicate("breakfast ?u - agent")

    # system['env'].add_predicate("weather_dealt")
    system['env'].add_predicate("dishes_dirty")

    # #hiking
    # system['env'].add_goal('(and (collected user backpack) (collected user compass) (collected user water_bottle) (outside user))')
    # #promenade
    # system['env'].add_goal('(and (collected user walking_stick) (collected user dog) (collected user water_bottle) (outside user))')
    # #watching_tv
    # system['env'].add_goal('(and (not (outside user)) (collected user water_bottle) (collected user sugar) (collected user tea) (collected user milk))')
    # # Baking Cake
    # system['env'].add_goal('(and (not (outside user)) (collected user sugar) (collected user chocolate) (collected user milk) (collected user flour))')

    system['env'].add_object('agent')
    system['env'].add_sub_objects('agent', 'user')

    system['env'].add_constants('weather')
    system['env'].add_sub_constants('weather', 'sunshine')
    system['env'].add_sub_constants('weather', 'hail')
    system['env'].add_sub_constants('weather', 'rainy')
    # system['env'].add_sub_constants('weather', 'cloudy')
    # system['env'].add_constants('time')
    # system['env'].add_sub_constants('time', 'morning')
    # system['env'].add_sub_constants('time', 'noon')
    # system['env'].add_sub_constants('time', 'evening')
    system['env'].add_constants('obj')
    system['env'].add_sub_constants('obj', 'backpack')
    system['env'].add_sub_constants('obj', 'water_bottle')
    system['env'].add_sub_constants('obj', 'tea')
    system['env'].add_sub_constants('obj', 'milk')
    system['env'].add_sub_constants('obj', 'sugar')

    #hiking
    system['env'].add_goal('(and (collected user backpack) (collected user water_bottle) (outside user))')
    #promenade
    system['env'].add_goal('(and (collected user backpack) (collected user tea) (outside user))')
    #watching_tv
    system['env'].add_goal('(and (not (outside user)) (collected user water_bottle) (collected user tea) (collected user sugar))')
    # Baking Cake
    system['env'].add_goal('(and (not (outside user)) (collected user backpack) (collected user sugar) (collected user milk))')
    # Readig Book
    system['env'].add_goal('(and (not (outside user)) (collected user tea) (collected user sugar) (collected user milk))')


    #relationship added
    # system['env'].add_common_knowledge(" after morning lunch " )
    # system['env'].add_common_knowledge(" after lunch after_noon " )
    # system['env'].add_common_knowledge(" after after_noon evening " )
    # system['env'].add_common_knowledge(" after evening night " )
    # system['env'].add_common_knowledge(" after night morning " )

    #ALSO add what is undesired situations to define which state will be undesired!
    system['emq'].des.add_situation('get_wet', ['(current_weather rainy)' , '(outside ?u - agent)'], 0.32)
    system['emq'].des.add_situation('get_hurt', ['(current_weather hail)' , '(outside ?u - agent)'], 0.0)
    system['emq'].des.add_situation('dirt_dishes', ['(dishes_dirty)'], 0.75)

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
    intent, intent_map, dynamic_k = system['recogniser'].recognize_intentions(list_of_goals, domain_name, problem_name)

    act_robot = system['env'].return_robot_action_list()
    unvoluntary_action_list = system['env'].return_unvoluntary_action_list()
    cur_state = system['env'].return_current_state()

    defined_action = system['env'].create_action_list_map(unvoluntary_action_list)

    '''
        EQM

        First create evolve_map - hypothetical map to forecast future
    '''

    #Define intention recogniton as opportunity
    effect_size_of_hir = 0.2 #desirability value

    K = 2

    ##########################################################
    evolve_map = system['emq'].create_evolve_map_define(cur_state, defined_action)
    hashmap_state = system['emq'].return_state_hash_map()

    oop_intent = system['emq'].oop.set_as_oop(intent_map, cur_state, defined_action, effect_size_of_hir)
    ###########
    opp_eqm = system['emq'].oop.findOpportunity(evolve_map, cur_state, act_robot, K)

    hashmap_state = system['emq'].return_state_hash_map()
    evolve_map = system['emq'].return_evolve_map()

    return opp_eqm, oop_intent, evolve_map, hashmap_state, react, intent_map, K

# def evolve_map_creation():
#
#     evolve_map = {}
#
#
#     hash_map = {}
#
#     #S0
#     hash_map['(current_weather sunshine);(current_time morning);(breakfast user)'] =  ['(current_weather sunshine)',
#     '(current_time morning)', '(breakfast user)']
#     evolve_map['(current_weather sunshine);(current_time morning);(breakfast user)'] = ['(current_weather sunshine);(current_time morning);(collected water_bottle);(dishes_dirty)',
#     '(current_weather sunshine);(current_time morning);(collected water_bottle)']
#
#     #S1.0
#     hash_map['(current_weather sunshine);(current_time morning);(collected water_bottle);(dishes_dirty)'] =  ['(current_weather sunshine)',
#     '(current_time morning)',  '(collected water_bottle)', '(dishes_dirty)']
#     evolve_map['(current_weather sunshine);(current_time morning);(collected water_bottle);(dishes_dirty)'] = [ #'(current_weather sunshine);(current_time morning);(collected water_bottle);(collected backpack);(dishes_dirty)',
#     '(current_weather sunshine);(current_time morning);(collected water_bottle)',
#     '(current_weather sunshine);(current_time morning);(collected water_bottle);(collected backpack)']
#
#     #S1.1
#     hash_map['(current_weather sunshine);(current_time morning);(collected water_bottle)'] =  ['(current_weather sunshine)',
#     '(current_time morning)', '(collected water_bottle)']
#     evolve_map['(current_weather sunshine);(current_time morning);(collected water_bottle)'] = ['(current_weather sunshine);(current_time morning);(collected water_bottle);(collected backpack)']
#
#
#     #S2.0
#     # hash_map['(current_weather sunshine);(current_time morning);(collected water_bottle);(collected backpack);(dishes_dirty)'] =  ['(current_weather sunshine)',
#     # '(current_time morning)', '(dishes_dirty)', '(collected water_bottle)', '(collected backpack)']
#     # evolve_map['(current_weather sunshine);(current_time morning);(collected water_bottle);(collected backpack);(dishes_dirty)'] = ['(current_weather sunshine);(current_time morning);(collected water_bottle);(collected backpack);(collected compass);(dishes_dirty)',
#     # '(current_weather sunshine);(current_time morning);(collected water_bottle);(collected backpack);(collected compass)']
#
#     #S2.1
#     hash_map['(current_weather sunshine);(current_time morning);(collected water_bottle);(collected backpack)'] =  ['(current_weather sunshine)',
#     '(current_time morning)', '(collected water_bottle)', '(collected backpack)']
#     evolve_map['(current_weather sunshine);(current_time morning);(collected water_bottle);(collected backpack)'] = ['(current_weather sunshine);(current_time morning);(collected water_bottle);(collected backpack);(collected compass)']
#
#
#     #S3.0
#     # hash_map['(current_weather sunshine);(current_time morning);(collected water_bottle);(collected backpack);(collected compass);(dishes_dirty)'] =  ['(current_weather sunshine)',
#     # '(current_time morning)', '(dishes_dirty)', '(collected water_bottle)', '(collected backpack)', '(collected compass)']
#     # evolve_map['(current_weather sunshine);(current_time morning);(collected water_bottle);(collected backpack);(collected compass);(dishes_dirty)'] = ['(current_weather sunshine);(current_time morning);(collected water_bottle);(collected backpack);(collected compass)',
#     # '(current_weather hail);(current_time noon);(collected water_bottle);(collected backpack);(collected compass);(outside user)',
#     # '(current_weather rainy);(current_time noon);(collected water_bottle);(collected backpack);(collected compass);(outside user)']
#
#     #S3.1
#     hash_map['(current_weather sunshine);(current_time morning);(collected water_bottle);(collected backpack);(collected compass)'] =  ['(current_weather sunshine)',
#     '(current_time morning)', '(collected water_bottle)', '(collected backpack)', '(collected compass)']
#     evolve_map['(current_weather sunshine);(current_time morning);(collected water_bottle);(collected backpack);(collected compass)'] = ['(current_weather hail);(current_time noon);(collected water_bottle);(collected backpack);(collected compass);(outside user)',
#     '(current_weather rainy);(current_time noon);(collected water_bottle);(collected backpack);(collected compass);(outside user)']
#
#
#     #S4.0
#     # hash_map['(current_weather hail);(current_time noon);(collected water_bottle);(collected backpack);(collected compass);(outside user)'] =  ['(current_weather hail)',
#     # '(current_time noon)', '(collected water_bottle)', '(collected backpack)', '(collected compass)', '(outside user)']
#     # evolve_map['(current_weather hail);(current_time noon);(collected water_bottle);(collected backpack);(collected compass);(outside user)'] = []
#
#     #S4.1
#     hash_map['(current_weather rainy);(current_time noon);(collected water_bottle);(collected backpack);(collected compass);(outside user)'] =  ['(current_weather rainy)',
#     '(current_time noon)', '(collected water_bottle)', '(collected backpack)', '(collected compass)', '(outside user)']
#     evolve_map['(current_weather rainy);(current_time noon);(collected water_bottle);(collected backpack);(collected compass);(outside user)'] = []
#
#     return evolve_map, hash_map


def executor(opp_emq):
    maxy = max(node.opportunity for node in opp_emq)
    maxarg = max(opp_emq, key=lambda node: node.opportunity)
    return maxy, maxarg

if __name__ =='__main__':
    print("Hello World!")

    # sys.stdout = open("/home/sara.buyukgoz/Desktop/proactive_robot_sim/results/23_09/eqm_s0.txt", "w")
    # try:
    setClasses()

    '''
       Please update the path name with your path name of fast_downward library
    '''

    # system['pla'].set_path('/Users/serabuyukgoz/Code/humanAi/planner')
    # system['pla'].set_python_version('3')

    system['pla'].set_path('~/planner/fast_downward/downward')
    system['pla'].set_python_version('3.6')
    '''
      Other search methods also could be use depend on the complexity of problem
      Such as; "astar(lmcut())" , "astar(ipdb())" ...
    '''
    system['pla'].set_search_method("astar(add())")

    domain_name, problem_name = create_world_state(system)

    # S0
    system['env'].add_state_change("(current_weather sunshine)")
    system['env'].add_state_change("(breakfast user)")

    #s1.0

    #add change in the world

    system['env'].add_state_change("(not (breakfast user))")
    system['env'].add_state_change("(dishes_dirty)")
    system['env'].add_state_change("(collected user water_bottle)")

    #s2.0

    #add change in the world

    system['env'].add_state_change("(collected user backpack)")


    # #s3.0
    #
    # #add change in the world
    #
    # system['env'].add_state_change("(collected user compass)")


    react = time.time()
    opp_emq, opp_hir, state_evolvation, hashmap, reaction_time, intent_map_res, K = updateSituation(system)
    react = time.time() - react


    eqm_max_value, eqm_max_arg = executor(opp_emq)
    oop = [*opp_emq, *opp_hir]
    hir_eqm_max_value, hir_eqm_max_arg = executor(oop)


    ############################################################################

#    print('Final Map --------')
    print_all(react, opp_emq, opp_hir, system)
    print("MAximised value {} : EQM Opportunity {} {} in {} ".format(eqm_max_value, eqm_max_arg.action, eqm_max_arg.opportunity_type, eqm_max_arg.k))
    print("MAximised value {} :  EQM + Intent Opportunity {} {} in {} ".format(hir_eqm_max_value, hir_eqm_max_arg.action, hir_eqm_max_arg.opportunity_type, hir_eqm_max_arg.k))

    print("Evolve Map")
    print_evolve_map(state_evolvation)
    # print_hash_map(hashmap)

    cur_state = system['env'].return_current_state()
    cur_state_object = system['emq'].return_object_of_state(cur_state)

    print("Intent Map: {}".format(intent_map_res))

    print("Calculation Time -> {}".format(reaction_time))
    print('Length = {}, {}'.format(len(state_evolvation[cur_state_object.name]),len(state_evolvation)))
    print('K = {}'.format(K))
    graph(state_evolvation, hashmap, cur_state_object.name)
    # except Exception as e:
    #     print("Main Exception")
    #     print(e)
