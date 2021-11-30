import os
import tempfile
import subprocess
import argparse
import copy
import sys

import time

from src.environment import Environment
from src.planner import Planner
from src.intention_recognition import Intention
from src.desireability import CalculateDesireability
from src.opportunity import OpportunityDetection
from src.equilibrium_maintenance import Equilibrium_Maintenance

from src.executor import SpeechHelper, make_application

from print_strategy import *
# from extract_graph import graph

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

def create_world_state(system):

    system['env'].add_type('main')
    system['env'].add_sub_types('main', 'obj')
    system['env'].add_sub_types('main', 'agent')
    system['env'].add_sub_types('main', 'weather')
    system['env'].add_sub_types('main', 'time')
    system['env'].add_sub_types('main', 'numeric')

    #adding agent's action for intention recognition

    system['env'].add_action("Human", "(?u - agent)", "(and (not(outside ?u)) (not (warned ?u)))", "(outside ?u)", "leave_home")
    system['env'].add_action("Human", "(?u - agent)", "(and (dishes_dirty) (not(outside ?u)) )", "(not(dishes_dirty))", "clean_dishes")
    system['env'].add_action("Human", "(?u - agent ?x - obj)", "(and (not(gathered ?u ?x)) (not(outside ?u)) )", "(gathered ?u ?x)", "collect")
    system['env'].add_action("Human", "(?u - agent ?x - obj)", "(and (gathered ?u ?x) (not(outside ?u)) )", "(not(gathered ?u ?x))", "leave")
    #added robot actions for equilibrium maintenance, all of robot's action is communicative

    system['env'].add_action("Robot", "(?u - agent)", "(and (dishes_dirty) (not(outside ?u)) )", "(not(dishes_dirty))", "tell_clean_dishes")
    system['env'].add_action("Robot", "(?u - agent ?x - obj)", "(and (not(gathered ?u ?x)) (not(outside ?u)) )", "(gathered robot ?x)", "tell_gather")
    # system['env'].add_action("Robot", "(?u - agent)", "(and (outside ?u) (current_weather hail))", "(not(outside ?u))", "warn_hail")
    system['env'].add_action("Robot", "(?u - agent)", "(and (not(outside ?u))", "(and (not(outside ?u)) (warned ?u))", "warn")

    #added actions for free run, changes of concepts!
    system['env'].add_action("Free", "(?wp - weather ?wn - weather)", "(current_weather ?wp)", "(and (not (current_weather ?wp)) (current_weather ?wn))", "weather_change")
    system['env'].add_action("Free", "(?u - agent)", "(breakfast ?u)", "(and  (not (breakfast ?u)) (dishes_dirty))", "had_breakfast")

    system['env'].add_predicate("gathered ?u - agent ?x - objects")
    system['env'].add_predicate("outside ?u - agent")
    system['env'].add_predicate("current_weather ?w - weather")
    system['env'].add_predicate("current_time ?t - time")
    system['env'].add_predicate("breakfast ?u - agent")
    system['env'].add_predicate("dishes_dirty")
    system['env'].add_predicate("watch_tv ?u - agent")
    system['env'].add_predicate("read_book ?u - agent")
    system['env'].add_predicate("warned ?u - agent")
    system['env'].add_predicate("temp ?n - numeric")

    system['env'].add_object('agent')
    system['env'].add_sub_objects('agent', 'user')
    # system['env'].add_sub_objects('agent', 'robot')
    system['env'].add_constants('numeric')
    system['env'].add_sub_constants('numeric', '0')
    system['env'].add_sub_constants('numeric', '1')
    system['env'].add_sub_constants('numeric', '2')
    system['env'].add_sub_constants('numeric', '3')
    system['env'].add_sub_constants('numeric', '4')
    system['env'].add_constants('time')
    system['env'].add_sub_constants('time', 'morning')
    system['env'].add_sub_constants('time', 'noon')
    system['env'].add_sub_constants('time', 'evening')
    system['env'].add_constants('weather')
    system['env'].add_sub_constants('weather', 'cloudy')
    system['env'].add_sub_constants('weather', 'sunshine')
    system['env'].add_sub_constants('weather', 'hail')
    system['env'].add_sub_constants('weather', 'rainy')
    system['env'].add_constants('obj')
    system['env'].add_sub_constants('obj', 'backpack')
    system['env'].add_sub_constants('obj', 'compass')
    system['env'].add_sub_constants('obj', 'water_bottle')
    system['env'].add_sub_constants('obj', 'tea')
    system['env'].add_sub_constants('obj', 'sugar')
    system['env'].add_sub_constants('obj', 'book')
    system['env'].add_sub_constants('obj', 'remote')
    system['env'].add_sub_constants('obj', 'hat')
    system['env'].add_sub_constants('obj', 'dog')


    #hiking
    system['env'].add_goal('(and (gathered user backpack) (gathered user water_bottle) (gathered user compass) (outside user))')
    #promenade
    system['env'].add_goal('(and (gathered user hat) (gathered user water_bottle) (gathered user dog)  (outside user))')
    #watching_tv
    system['env'].add_goal('(and (not (outside user)) (gathered user water_bottle) (gathered user compass) (gathered user dog) (gathered user remote))')
    # Readig Book
    system['env'].add_goal('(and (not (outside user)) (gathered user backpack) (gathered user book) (gathered user tea) (gathered user sugar))')

    #relationship added
    system['env'].add_common_knowledge(" after morning noon " )
    system['env'].add_common_knowledge(" after noon evening " )
    system['env'].add_common_knowledge(" after night morning " )

    #ALSO add what is undesired situations to define which state will be undesired!
    system['emq'].des.add_situation('get_wet', ['(current_weather rainy)' , '(outside user)'], 0.4)
    system['emq'].des.add_situation('get_hurt', ['(current_weather hail)' , '(outside user)'], 0.0)
    system['emq'].des.add_situation('dirt_dishes', ['(dishes_dirty)'], 0.6)

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
    effect_size_of_hir = 0.5 #desirability value

    K = 2
    #
    # evolve_map, hashmap_state, des_map = evolve_map_creation()
    # system['emq'].set_env(evolve_map, hashmap_state)
    # system['emq'].des.add_des_map(des_map)
    #
    # hashmap_state = system['emq'].return_state_hash_map()
    # evolve_map = system['emq'].return_evolve_map()
    # setDesirability(hashmap_state, des_map)

    evolve_map = system['emq'].fuction_F_k(temp, cur_state)

    raise Exception('Check map')

    oop_intent = system['emq'].oop.set_as_oop(intent_map, cur_state, defined_action, effect_size_of_hir)
    ###########
    opp_eqm = system['emq'].oop.findOpportunity(evolve_map, cur_state, act_robot, K)

    hashmap_state = system['emq'].return_state_hash_map()
    evolve_map = system['emq'].return_evolve_map()

    return des_map, opp_eqm, oop_intent, evolve_map, hashmap_state, react, intent_map, K

def setDesirability(hashmap_state, des):
    for each_state in hashmap_state:
        each_state_object = hashmap_state[each_state]
        each_state_object.setStateDesirability(des[each_state_object.name])

def free_map():
    rules = {}
    rules[0] = [rule1 , rule2]
    rule1 = [temp]
    temp = {'pre' : ['(temp 0)'],
            'eff' : ['(not (temp 0))', '(temp 1)']
          }

def choose(opp_emq):
    maxy = max(node.opportunity for node in opp_emq)
    maxarg = max(opp_emq, key=lambda node: node.opportunity)
    return maxy, maxarg

if __name__ =='__main__':
    print("Hello World!")

    #Robot talk executor
    app = make_application()
    app.start()

    helper = SpeechHelper(app.session)
    helper.talk('Hello')
    #

    # sys.stdout = open("/home/sara.buyukgoz/Desktop/proactive_robot_sim/results/23_09/eqm_s0.txt", "w")
    # try:
    setClasses()

    '''
       Please update the path name with your path name of fast_downward library
    '''

    # system['pla'].set_path('/Users/serabuyukgoz/Code/humanAi/planner')
    # system['pla'].set_python_version('3')
    #
    system['pla'].set_path('~/planner/fast_downward/downward')
    system['pla'].set_python_version('3.6')
    '''
      Other search methods also could be use depend on the complexity of problem
      Such as; "astar(lmcut())" , "astar(ipdb())" ...
    '''
    system['pla'].set_search_method("astar(add())")

    domain_name, problem_name = create_world_state(system)

    # S0
    system['env'].add_state_change("(temp 0)")
    system['env'].add_state_change("(current_weather sunshine)")
    system['env'].add_state_change("(current_time morning)")
    system['env'].add_state_change("(breakfast user)")

    #s1.0

    # # add change in the world
    # # # # #
    # system['env'].add_state_change("(not (breakfast user))")
    # system['env'].add_state_change("(dishes_dirty)")
    # system['env'].add_state_change("(gathered user backpack)")
    # #
    # # #s2.0
    # # #
    # # #add change in the world
    # system['env'].add_state_change("(not (dishes_dirty))")
    # system['env'].add_state_change("(gathered user compass)")
    # # # #
    # # # # S3.0
    # # system['env'].add_state_change("(not (current_weather sunshine))")
    # # system['env'].add_state_change("(current_weather cloudy)")
    # system['env'].add_state_change("(gathered user water_bottle)")

    desirability_map, opp_emq, opp_hir, state_evolvation, hashmap, reaction_time, intent_map_res, K = updateSituation(system)

    eqm_max_value, eqm_max_arg, text = choose(opp_emq)
    oop = [*opp_emq, *opp_hir]
    hir_eqm_max_value, hir_eqm_max_arg, text = choose(oop)
    helper.talk(text)


    ############################################################################

#    print('Final Map --------')
    print_all(react, opp_emq, opp_hir, system)
    print("Maximised value {} : EQM Opportunity {} {} in {} ".format(eqm_max_value, eqm_max_arg.action, eqm_max_arg.opportunity_type, eqm_max_arg.k))
    print("Maximised value {} : Late-Fusion Opportunity {} {} in {} ".format(hir_eqm_max_value, hir_eqm_max_arg.action, hir_eqm_max_arg.opportunity_type, hir_eqm_max_arg.k))

    print("Evolve Map")
    print_evolve_map(state_evolvation, hashmap)
    # print_hash_map(hashmap)

    cur_state = system['env'].return_current_state()
    cur_state_object = system['emq'].return_object_of_state(cur_state)

    print("Intent Map: {}".format(intent_map_res))

    print("Calculation Time -> {}".format(reaction_time))
    print('Length = {}, {}'.format(len(state_evolvation[cur_state_object.name]),len(state_evolvation)))
    print('K = {}'.format(K))
    # graph(state_evolvation, hashmap, cur_state_object.name)
    # except Exception as e:
    #     print("Main Exception")
    #     print(e)
