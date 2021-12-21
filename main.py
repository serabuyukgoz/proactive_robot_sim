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
from src.equilibrium_maintenance import Equilibrium_Maintenance, Situation

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
    system['env'].add_type('agent')
    system['env'].add_sub_types('agent', 'human')
    system['env'].add_sub_types('agent', 'robot')

    #adding agent's action for intention recognition

    system['env'].add_action("Human", "(?u - human)", "(and (not(outside ?u)) (not (warned ?u)))", "(outside ?u)", "leave_home")
    system['env'].add_action("Human", "(?u - human)", "(and (dishes_dirty) (not(outside ?u)) )", "(not(dishes_dirty))", "clean_dishes")
    system['env'].add_action("Human", "(?u - human ?x - obj)", "(and (not(gathered ?u ?x)) (not(outside ?u)) )", "(gathered ?u ?x)", "gather")
    system['env'].add_action("Human", "(?u - human ?x - obj)", "(and (gathered ?u ?x) (not(outside ?u)) )", "(not(gathered ?u ?x))", "leave")
    #added robot actions for equilibrium maintenance, all of robot's action is communicative

    system['env'].add_action("Robot", "(?u - human)", "(and (dishes_dirty) (not(outside ?u)) )", "(not(dishes_dirty))", "tell_clean_dishes")
    system['env'].add_action("Robot", "(?u - human ?x - obj)", "(and (not(gathered ?u ?x)) (not(outside ?u)) )", "(gathered pepper ?x)", "tell_gather")
    # system['env'].add_action("Robot", "(?u - agent)", "(and (outside ?u) (current_weather hail))", "(not(outside ?u))", "warn_hail")
    system['env'].add_action("Robot", "(?u - human)", "(and (not(outside ?u))", "(and (not(outside ?u)) (warned ?u))", "warn")

    #added actions for free run, changes of concepts!
    system['env'].add_action("Free", "(?wp - weather ?wn - weather)", "(current_weather ?wp)", "(and (not (current_weather ?wp)) (current_weather ?wn))", "weather_change")
    system['env'].add_action("Free", "(?u - human)", "(breakfast ?u)", "(and  (not (breakfast ?u)) (dishes_dirty))", "had_breakfast")

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

    system['env'].add_object('human')
    system['env'].add_object('robot')
    system['env'].add_sub_objects('human', 'user')
    system['env'].add_sub_objects('robot', 'pepper')
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
    # system['emq'].des.add_situation('get_wet', ['(current_weather rainy)' , '(outside user)'], 0.4)
    # system['emq'].des.add_situation('get_hurt', ['(current_weather hail)' , '(outside user)'], 0.001)
    # system['emq'].des.add_situation('dirt_dishes', ['(dishes_dirty)'], 0.6)
    # system['emq'].des.add_situation('collect_backpack', ['(gathered pepper backpack)'], 0.01)
    # system['emq'].des.add_situation('collect_compass', ['(gathered pepper compass)'], 0.01)
    # system['emq'].des.add_situation('collect_water_bottle', ['(gathered pepper water_bottle)'], 0.01)
    # system['emq'].des.add_situation('collect_tea', ['(gathered pepper tea)'], 0.01)
    # system['emq'].des.add_situation('collect_sugar', ['(gathered pepper sugar)'], 0.01)
    # system['emq'].des.add_situation('collect_book', ['(gathered pepper book)'], 0.01)
    # system['emq'].des.add_situation('collect_remote', ['(gathered pepper remote)'], 0.01)
    # system['emq'].des.add_situation('collect_hat', ['(gathered pepper hat)'], 0.01)
    # system['emq'].des.add_situation('collect_dog', ['(gathered pepper dog)'], 0.01)

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
    intent_list, intent_map, dynamic_k = system['recogniser'].recognize_intentions(list_of_goals, domain_name, problem_name)
    intended_action, intention, intention_plan = system['recogniser'].hir(intent_map)

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
    #
    hashmap_state, des_map = set_des_map()
    system['emq'].set_hashmap(hashmap_state, des_map)
    system['emq'].des.add_des_map(des_map)

    hashmap_state = system['emq'].return_state_hash_map()

    free_map_data = free_map()
    evolve_map = system['emq'].fuction_F_k(free_map_data, cur_state)

    hashmap_state = system['emq'].return_state_hash_map()
    # evolve_map = system['emq'].return_evolve_map()

    print("--------------------------------")
    print_hash_map(hashmap_state)
    print("--------------------------------")
    print_evolve_map(evolve_map)

    oop_intent = system['emq'].oop.set_as_oop(intended_action, cur_state, defined_action, effect_size_of_hir)

    ###########

    opp_eqm = system['emq'].oop.findOpportunity(evolve_map, cur_state, act_robot, K)

    hashmap_state = system['emq'].return_state_hash_map()
    evolve_map = system['emq'].return_evolve_map()

    return opp_eqm, oop_intent, evolve_map, hashmap_state, intent_map, K

def set_des_map():

    hash_map = {}
    des_map ={}


    hash_map['S0'] = ['(temp 0)', '(current_weather sunshine)', '(current_time morning)', '(breakfast user)']
    hash_map['S1.0'] = ['(temp 1)', '(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(dishes_dirty)']
    hash_map['S1.1'] = ['(temp 1)', '(current_weather sunshine)', '(current_time morning)', '(dishes_dirty)']
    hash_map['S2.0'] = ['(temp 2)', '(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)']
    hash_map['S2.1'] = ['(temp 2)', '(current_weather sunshine)', '(current_time morning)', '(gathered user hat)']
    hash_map['S3.0'] = ['(temp 3)', '(current_weather cloudy)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)']
    hash_map['S3.1'] = ['(temp 3)', '(current_weather cloudy)', '(current_time morning)', '(gathered user hat)', '(gathered user dog)']

    hash_map['S4.0'] = ['(temp 4)', '(current_weather hail)', '(current_time noon)', '(outside user)']

    hash_map['S4.1'] = ['(temp 4)', '(current_weather rainy)', '(current_time noon)', '(outside user)']


    hash_map['S0.safe'] = ['(temp 0)','(current_weather sunshine)', '(current_time morning)', '(breakfast user)', '(warned user)']
    hash_map['S1.0.safe'] = ['(temp 1)','(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(dishes_dirty)', '(warned user)']
    hash_map['S1.1.safe'] = ['(temp 1)','(current_weather sunshine)', '(current_time morning)', '(dishes_dirty)', '(warned user)']
    hash_map['S2.0.safe'] = ['(temp 2)','(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(warned user)']

    hash_map['S2.x.safe'] = ['(temp 2)','(current_weather sunshine)', '(current_time morning)', '(book_reading user)', '(warned user)']
    hash_map['S2.y.safe'] = ['(temp 2)','(current_weather sunshine)', '(current_time morning)', '(watch_tv user)', '(warned user)']
    hash_map['S2.1.safe'] = ['(temp 2)','(current_weather sunshine)', '(current_time morning)', '(gathered user sugar)', '(warned user)']
    hash_map['S3.0.safe'] = ['(temp 3)', '(current_weather cloudy)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)', '(warned user)']
    hash_map['S3.1.safe'] = ['(temp 3)', '(current_weather cloudy)', '(current_time morning)', '(gathered user hat)', '(gathered user dog)', '(warned user)']

    hash_map['S0.cbp'] = ['(temp 0)','(current_weather sunshine)', '(current_time morning)', '(breakfast user)' , '(gathered pepper backpack)']
    hash_map['S0.cb'] = ['(temp 0)','(current_weather sunshine)', '(current_time morning)', '(breakfast user)' , '(gathered pepper book)']
    hash_map['S0.cr'] = ['(temp 0)','(current_weather sunshine)', '(current_time morning)', '(breakfast user)' , '(gathered pepper remote)']
    hash_map['S0.cwb'] = ['(temp 0)','(current_weather sunshine)', '(current_time morning)', '(breakfast user)' , '(gathered pepper water_bottle)']
    hash_map['S0.ct'] = ['(temp 0)','(current_weather sunshine)', '(current_time morning)', '(breakfast user)' , '(gathered pepper tea)']
    hash_map['S0.cc'] = ['(temp 0)','(current_weather sunshine)', '(current_time morning)', '(breakfast user)' , '(gathered pepper compass)']
    hash_map['S0.cs'] = ['(temp 0)','(current_weather sunshine)', '(current_time morning)', '(breakfast user)' , '(gathered pepper sugar)']
    hash_map['S0.ch'] = ['(temp 0)','(current_weather sunshine)', '(current_time morning)', '(breakfast user)' , '(gathered pepper hat)']
    hash_map['S0.cd'] = ['(temp 0)','(current_weather sunshine)', '(current_time morning)', '(breakfast user)' , '(gathered pepper dog)']
    hash_map['S0.o'] = ['(temp 0)','(current_weather sunshine)', '(current_time morning)', '(breakfast user)' , '(outside user)']

    hash_map['S1.0.cwb'] = ['(temp 1)', '(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(dishes_dirty)', '(gathered pepper water_bottle)']
    hash_map['S1.0.ct'] = ['(temp 1)', '(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(dishes_dirty)', '(gathered pepper tea)']
    hash_map['S1.0.cc'] = ['(temp 1)', '(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(dishes_dirty)', '(gathered pepper compass)']
    hash_map['S1.0.cs'] = ['(temp 1)', '(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(dishes_dirty)', '(gathered pepper sugar)']
    hash_map['S1.0.dc'] = ['(temp 1)', '(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)']
    hash_map['S1.0.cb'] = ['(temp 1)', '(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(dishes_dirty)', '(gathered pepper book)']
    hash_map['S1.0.cr'] = ['(temp 1)', '(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(dishes_dirty)', '(gathered pepper remote)']
    hash_map['S1.0.ch'] = ['(temp 1)', '(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(dishes_dirty)', '(gathered pepper hat)']
    hash_map['S1.0.cd'] = ['(temp 1)', '(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(dishes_dirty)', '(gathered pepper dog)']
    hash_map['S1.0.o'] = ['(temp 1)', '(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(dishes_dirty)', '(outside user)']

    hash_map['S1.1.cbp'] = ['(temp 1)', '(current_weather sunshine)', '(current_time morning)', '(dishes_dirty)' , '(gathered pepper backpack)']
    hash_map['S1.1.cb'] = ['(temp 1)', '(current_weather sunshine)', '(current_time morning)', '(dishes_dirty)' , '(gathered pepper book)']
    hash_map['S1.1.cb'] = ['(temp 1)', '(current_weather sunshine)', '(current_time morning)', '(dishes_dirty)' , '(gathered pepper remote)']
    hash_map['S1.1.cwb'] = ['(temp 1)', '(current_weather sunshine)', '(current_time morning)', '(dishes_dirty)', '(gathered pepper water_bottle)']
    hash_map['S1.1.ct'] = ['(temp 1)', '(current_weather sunshine)', '(current_time morning)', '(dishes_dirty)', '(gathered pepper tea)']
    hash_map['S1.1.cc'] = ['(temp 1)', '(current_weather sunshine)', '(current_time morning)', '(dishes_dirty)', '(gathered pepper compass)']
    hash_map['S1.1.cs'] = ['(temp 1)', '(current_weather sunshine)', '(current_time morning)', '(dishes_dirty)', '(gathered pepper sugar)']
    hash_map['S1.1.dc'] = ['(temp 1)', '(current_weather sunshine)', '(current_time morning)']
    hash_map['S1.1.ch'] = ['(temp 1)', '(current_weather sunshine)', '(current_time morning)', '(dishes_dirty)', '(gathered pepper hat)']
    hash_map['S1.1.cd'] = ['(temp 1)', '(current_weather sunshine)', '(current_time morning)', '(dishes_dirty)', '(gathered pepper dog)']

    hash_map['S2.0.cwb'] = ['(temp 2)', '(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered pepper water_bottle)']
    hash_map['S2.0.ct'] = ['(temp 2)', '(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered pepper tea)']
    hash_map['S2.0.cs'] = ['(temp 2)', '(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered pepper sugar)']
    hash_map['S2.0.cb'] = ['(temp 2)', '(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered pepper book)']
    hash_map['S2.0.cr'] = ['(temp 2)', '(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered pepper remote)']
    hash_map['S2.0.ch'] = ['(temp 2)', '(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered pepper hat)']
    hash_map['S2.0.cd'] = ['(temp 2)', '(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered pepper dog)']

    hash_map['S2.1.cbp'] = ['(temp 2)', '(current_weather sunshine)', '(current_time morning)', '(gathered user hat)', '(gathered pepper backpack)']
    hash_map['S2.1.cwb'] = ['(temp 2)', '(current_weather sunshine)', '(current_time morning)', '(gathered user hat)', '(gathered pepper water_bottle)']
    hash_map['S2.1.ct'] = ['(temp 2)', '(current_weather sunshine)', '(current_time morning)', '(gathered user hat)', '(gathered pepper tea)']
    hash_map['S2.1.cc'] = ['(temp 2)', '(current_weather sunshine)', '(current_time morning)', '(gathered user hat)', '(gathered pepper compass)']
    hash_map['S2.1.o'] = ['(temp 2)', '(current_weather sunshine)', '(current_time morning)', '(gathered user hat)', '(outside user)']
    hash_map['S2.1.cb'] = ['(temp 2)', '(current_weather sunshine)', '(current_time morning)', '(gathered user hat)', '(gathered pepper book)']
    hash_map['S2.1.cr'] = ['(temp 2)', '(current_weather sunshine)', '(current_time morning)', '(gathered user hat)', '(gathered pepper remote)']
    hash_map['S2.1.ch'] = ['(temp 2)', '(current_weather sunshine)', '(current_time morning)', '(gathered user hat)', '(gathered pepper sugar)']
    hash_map['S2.1.cd'] = ['(temp 2)', '(current_weather sunshine)', '(current_time morning)', '(gathered user hat)', '(gathered pepper dog)']

    hash_map['S3.0.ct'] = ['(temp 3)', '(current_weather cloudy)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)', '(gathered pepper tea)']
    hash_map['S3.0.cs'] = ['(temp 3)', '(current_weather cloudy)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)', '(gathered pepper sugar)']
    hash_map['S3.0.o'] = ['(temp 3)', '(current_weather cloudy)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)', '(outside user)']
    hash_map['S3.0.cb'] = ['(temp 3)', '(current_weather cloudy)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)', '(gathered pepper book)']
    hash_map['S3.0.cr'] = ['(temp 3)', '(current_weather cloudy)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)', '(gathered pepper remote)']
    hash_map['S3.0.ch'] = ['(temp 3)', '(current_weather cloudy)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)', '(gathered pepper hat)']
    hash_map['S3.0.cd'] = ['(temp 3)', '(current_weather cloudy)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)', '(gathered pepper dog)']


    hash_map['S3.1.cbp'] = ['(temp 3)', '(current_weather cloudy)', '(current_time morning)', '(gathered user hat)', '(gathered user dog)', '(gathered pepper backpack)']
    hash_map['S3.1.cwb'] = ['(temp 3)', '(current_weather cloudy)', '(current_time morning)', '(gathered user hat)', '(gathered user dog)', '(gathered pepper water_bottle)']
    hash_map['S3.1.cc'] = ['(temp 3)', '(current_weather cloudy)', '(current_time morning)', '(gathered user hat)', '(gathered user dog)', '(gathered pepper compass)']
    hash_map['S3.1.o'] = ['(temp 3)', '(current_weather cloudy)', '(current_time morning)', '(gathered user hat)', '(gathered user dog)', '(outside user)']
    hash_map['S3.1.cb'] = ['(temp 3)', '(current_weather cloudy)', '(current_time morning)', '(gathered user hat)', '(gathered user dog)', '(gathered pepper book)']
    hash_map['S3.1.cr'] = ['(temp 3)', '(current_weather cloudy)', '(current_time morning)', '(gathered user hat)', '(gathered user dog)', '(gathered pepper remote)']
    hash_map['S3.1.ch'] = ['(temp 3)', '(current_weather cloudy)', '(current_time morning)', '(gathered user hat)', '(gathered user dog)', '(gathered pepper tea)']
    hash_map['S3.1.cd'] = ['(temp 3)', '(current_weather cloudy)', '(current_time morning)', '(gathered user hat)', '(gathered user dog)', '(gathered pepper sugar)']

    hash_map['S4.0'] = ['(temp 4)', '(current_weather hail)', '(current_time noon)', '(outside user)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)']
    hash_map['S4.0.safe'] = ['(temp 4)', '(current_weather hail)', '(current_time noon)', '(warned user)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)']
    hash_map['S4.0.cbp'] = ['(temp 4)', '(current_weather hail)', '(current_time noon)', '(outside user)', '(gathered pepper backpack)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)']
    hash_map['S4.0.cwb'] = ['(temp 4)', '(current_weather hail)', '(current_time noon)', '(outside user)', '(gathered pepper water_bottle)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)']
    hash_map['S4.0.ct'] = ['(temp 4)', '(current_weather hail)', '(current_time noon)', '(outside user)', '(gathered pepper tea)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)']
    hash_map['S4.0.cc'] = ['(temp 4)', '(current_weather hail)', '(current_time noon)', '(outside user)', '(gathered pepper compass)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)']
    hash_map['S4.0.cs'] = ['(temp 4)', '(current_weather hail)', '(current_time noon)', '(outside user)', '(gathered pepper sugar)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)']
    hash_map['S4.0.cb'] = ['(temp 4)', '(current_weather hail)', '(current_time noon)', '(outside user)', '(gathered pepper book)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)']
    hash_map['S4.0.cr'] = ['(temp 4)', '(current_weather hail)', '(current_time noon)', '(outside user)', '(gathered pepper remote)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)']
    hash_map['S4.0.ch'] = ['(temp 4)', '(current_weather hail)', '(current_time noon)', '(outside user)', '(gathered pepper hat)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)']
    hash_map['S4.0.cd'] = ['(temp 4)', '(current_weather hail)', '(current_time noon)', '(outside user)', '(gathered pepper dog)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)']

    hash_map['S4.1'] = ['(temp 4)', '(current_weather rainy)', '(current_time noon)', '(outside user)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)']
    hash_map['S4.1.safe'] = ['(temp 4)','(current_weather rainy)', '(current_time noon)', '(warned user)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)']
    hash_map['S4.1.cbp'] = ['(temp 4)','(current_weather rainy)', '(current_time noon)', '(outside user)', '(gathered pepper backpack)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)']
    hash_map['S4.1.cwb'] = ['(temp 4)','(current_weather rainy)', '(current_time noon)', '(outside user)', '(gathered pepper water_bottle)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)']
    hash_map['S4.1.ct'] = ['(temp 4)','(current_weather rainy)', '(current_time noon)', '(outside user)', '(gathered pepper tea)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)']
    hash_map['S4.1.cc'] = ['(temp 4)','(current_weather rainy)', '(current_time noon)', '(outside user)', '(gathered pepper compass)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)']
    hash_map['S4.1.cs'] = ['(temp 4)','(current_weather rainy)', '(current_time noon)', '(outside user)', '(gathered pepper sugar)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)']
    hash_map['S4.1.cb'] = ['(temp 4)','(current_weather rainy)', '(current_time noon)', '(outside user)', '(gathered pepper book)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)']
    hash_map['S4.1.cr'] = ['(temp 4)','(current_weather rainy)', '(current_time noon)', '(outside user)', '(gathered pepper remote)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)']
    hash_map['S4.1.ch'] = ['(temp 4)','(current_weather rainy)', '(current_time noon)', '(outside user)', '(gathered pepper hat)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)']
    hash_map['S4.1.cd'] = ['(temp 4)','(current_weather rainy)', '(current_time noon)', '(outside user)', '(gathered pepper dog)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)']


    des_map['S0'] = 1.0
    des_map['S1.0'] = 0.8
    des_map['S1.1'] = 0.6
    des_map['S2.0'] = 1.0
    des_map['S2.x'] = 1.0
    des_map['S2.y'] = 1.0
    des_map['S2.1'] = 1.0
    des_map['S3.0'] = 1.0
    des_map['S3.1'] = 1.0
    des_map['S4.0'] = 0
    des_map['S4.1'] = 0.4

    des_map['S0.cb'] = 0.9
    des_map['S0.cbp'] = 0.9
    des_map['S0.cr'] = 0.9
    des_map['S0.cwb'] = 0.9
    des_map['S0.ct'] = 0.9
    des_map['S0.cc'] = 0.9
    des_map['S0.cs'] = 0.9
    des_map['S0.ch'] = 0.9
    des_map['S0.cd'] = 0.9
    des_map['S0.o'] = 0.9

    des_map['S1.0.cwb'] = 0.01
    des_map['S1.0.cb'] = 0.01
    des_map['S1.0.cr'] = 0.01
    des_map['S1.0.ct'] = 0.01
    des_map['S1.0.cc'] = 0.01
    des_map['S1.0.cs'] = 0.01
    des_map['S1.0.ch'] = 0.01
    des_map['S1.0.cd'] = 0.01
    des_map['S1.0.dc'] = 1.0
    des_map['S1.0.o'] = 0.01

    des_map['S1.1.cbp'] =  0.01
    des_map['S1.1.cb'] =  0.01
    des_map['S1.1.cr'] =  0.01
    des_map['S1.1.cwb'] =  0.01
    des_map['S1.1.ct'] =  0.01
    des_map['S1.1.cc'] =  0.01
    des_map['S1.1.cs'] =  0.01
    des_map['S1.1.ch'] =  0.01
    des_map['S1.1.cd'] =  0.01
    des_map['S1.1.dc'] = 1.0
    des_map['S1.1.o'] =  0.01

    des_map['S2.0.cwb'] = 0.01
    des_map['S2.0.cb'] = 0.01
    des_map['S2.0.cr'] = 0.01
    des_map['S2.0.ct'] = 0.01
    des_map['S2.0.cs'] = 0.01
    des_map['S2.0.o'] = 0.01
    des_map['S2.0.ch'] = 0.01
    des_map['S2.0.cd'] = 0.01

    # des_map['S2.x.cb'] = 0.5
    # des_map['S2.x.cbp'] = 0.5
    # des_map['S2.x.cr'] = 0.5
    # des_map['S2.x.cwb'] = 0.5
    # des_map['S2.x.ct'] = 0.5
    # des_map['S2.x.cc'] = 0.5
    # des_map['S2.x.cs'] = 0.5
    # des_map['S2.x.o'] = 0.5
    #
    # des_map['S2.y.cb'] = 0.5
    # des_map['S2.y.cbp'] = 0.5
    # des_map['S2.y.cr'] = 0.5
    # des_map['S2.y.cwb'] = 0.5
    # des_map['S2.y.ct'] = 0.5
    # des_map['S2.y.cc'] = 0.5
    # des_map['S2.y.cs'] = 0.5
    # des_map['S2.y.o'] = 0.5

    des_map['S2.1.cb'] = 0.01
    des_map['S2.1.cr'] = 0.01
    des_map['S2.1.cbp'] = 0.01
    des_map['S2.1.cwb'] = 0.01
    des_map['S2.1.ct'] = 0.01
    des_map['S2.1.cc'] = 0.01
    des_map['S2.1.ch'] = 0.01
    des_map['S2.1.cd'] = 0.01
    des_map['S2.1.o'] = 0.01

    des_map['S3.0.ct'] = 0.01
    des_map['S3.0.cr'] = 0.01
    des_map['S3.0.cb'] = 0.01
    des_map['S3.0.cs'] = 0.01
    des_map['S3.0.ch'] = 0.01
    des_map['S3.0.cd'] = 0.01
    des_map['S3.0.o'] = 0.01

    des_map['S3.1.cb'] = 0.01
    des_map['S3.1.cbp'] = 0.01
    des_map['S3.1.r'] = 0.01
    des_map['S3.1.cwb'] = 0.01
    des_map['S3.1.cc'] = 0.01
    des_map['S3.1.o'] = 0.01
    des_map['S3.1.cr'] = 0.01
    des_map['S3.1.ch'] = 0.01
    des_map['S3.1.cd'] = 0.01

    des_map['S4.0.safe'] = 1.0
    des_map['S4.0.cbp'] = 0.01
    des_map['S4.0.cr'] = 0.01
    des_map['S4.0.cb'] = 0.01
    des_map['S4.0.cwb'] = 0.01
    des_map['S4.0.ct'] = 0.1
    des_map['S4.0.cc'] = 0.1
    des_map['S4.0.cs'] = 0.1
    des_map['S4.0.ch'] = 0.1
    des_map['S4.0.cd'] = 0.1

    des_map['S4.1.safe'] = 1.0
    des_map['S4.1.cb'] = 0.01
    des_map['S4.1.cbp'] = 0.01
    des_map['S4.1.cr'] = 0.01
    des_map['S4.1.cwb'] = 0.01
    des_map['S4.1.ct'] = 0.01
    des_map['S4.1.cc'] = 0.01
    des_map['S4.1.cs'] = 0.01
    des_map['S4.1.ch'] = 0.01
    des_map['S4.1.cd'] = 0.01

    des_map['S0.safe'] = 0
    des_map['S1.0.safe'] = 0
    des_map['S1.1.safe'] = 0
    des_map['S2.0.safe'] = 0
    des_map['S2.x.safe'] = 0
    des_map['S2.y.safe'] = 0
    des_map['S2.1.safe'] = 0
    des_map['S3.0.safe'] = 0
    des_map['S3.1.safe'] = 0

    return hash_map, des_map

def free_map():
    rules = {}
    rules[1] = [[Situation(['(temp 0)'], ['(not (temp 0))', '(temp 1)']) ,
                    Situation(['(breakfast user)'], ['(not (breakfast user))', '(dishes_dirty)']),
                    Situation(['(not (gathered user backpack))'], ['(gathered user backpack)'])
                    ],
                [Situation(['(temp 0)'], ['(not (temp 0))', '(temp 1)']) ,
                    Situation(['(breakfast user)'], ['(not (breakfast user))', '(dishes_dirty)'])]]
    rules[2] = [[Situation(['(temp 1)'], ['(not (temp 1))', '(temp 2)']) ,
                    Situation(['(dishes_dirty)'], ['(not (dishes_dirty))']),
                    Situation(['(gathered user backpack)'], ['(gathered user compass)']),
                    Situation(['(not (gathered user backpack))',
                               '(not (gathered user compass))',
                               '(not (gathered user water_bottle))',
                               '(not (gathered user tea))',
                               '(not (gathered user sugar))',
                               '(not (gathered user book))',
                               '(not (gathered user remote))',
                               '(not (gathered user hat))',
                               '(not (gathered user dog))'],['(gathered user hat)'])]]
    rules[3] = [[Situation(['(temp 2)'], ['(not (temp 2))', '(temp 3)']) ,
                Situation(['(current_weather sunshine)'], ['(not (current_weather sunshine))', '(current_weather cloudy)']),
                Situation(['(gathered user backpack)', '(gathered user compass)'], ['(gathered user water_bottle)']),
                Situation(['(gathered user hat)'], ['(gathered user dog)'])
                ]]
    rules[4] = [[Situation(['(temp 3)'], ['(not (temp 3))', '(temp 4)']) ,
                Situation(['(and (not ((warned user))) (not (outside user)))'], ['(outside user)']),
                Situation(['(current_weather cloudy)'], ['(not (current_weather cloudy))', '(current_weather hail)']),
                Situation(['(current_time morning)'], ['(not (current_time morning))', '(current_time noon)'])],
                [Situation(['(temp 3)'], ['(not (temp 3))', '(temp 4)']) ,
                Situation(['(and (not ((warned user))) (not (outside user)))'], ['(outside user)']),
                Situation(['(current_weather cloudy)'], ['(not (current_weather cloudy))', '(current_weather rainy)']),
                Situation(['(current_time morning)'], ['(not (current_time morning))', '(current_time noon)'])]]




    return rules

def choose(opp_emq):
    maxy = max(node.opportunity for node in opp_emq)
    maxarg = max(opp_emq, key=lambda node: node.opportunity)
    text = "I have an opportunity"
    return maxy, maxarg, text

if __name__ =='__main__':
    print("Hello World!")

    #Robot talk executor
    # app = make_application()
    # app.start()
    #
    # helper = SpeechHelper(app.session)
    # helper.talk('Hello')
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
    #
    # # # add change in the world
    # # # # #
    system['env'].add_state_change("(not (temp 0))")
    system['env'].add_state_change("(temp 1)")
    system['env'].add_state_change("(not (breakfast user))")
    system['env'].add_state_change("(dishes_dirty)")
    system['env'].add_state_change("(gathered user backpack)")
    # #
    # # #s2.0
    # # #
    # # #add change in the world
    system['env'].add_state_change("(not (temp 1))")
    system['env'].add_state_change("(temp 2)")
    system['env'].add_state_change("(not (dishes_dirty))")
    system['env'].add_state_change("(gathered user compass)")
    # # # # #
    # # # # # S3.0
    system['env'].add_state_change("(not (temp 2))")
    system['env'].add_state_change("(temp 3)")
    system['env'].add_state_change("(not (current_weather sunshine))")
    system['env'].add_state_change("(current_weather cloudy)")
    system['env'].add_state_change("(gathered user water_bottle)")

    opp_emq, opp_hir, state_evolvation, hashmap, intent_map_res, K = updateSituation(system)

    eqm_max_value, eqm_max_arg, text = choose(opp_emq)
    oop = [*opp_emq, *opp_hir]
    hir_eqm_max_value, hir_eqm_max_arg, text = choose(oop)
    # helper.talk(text)


    ############################################################################

#    print('Final Map --------')
    print_all(opp_emq, opp_hir, system)
    print("Maximised value {} : EQM Opportunity {} {} in {} ".format(eqm_max_value, eqm_max_arg.action, eqm_max_arg.opportunity_type, eqm_max_arg.k))
    print("Maximised value {} : Late-Fusion Opportunity {} {} in {} ".format(hir_eqm_max_value, hir_eqm_max_arg.action, hir_eqm_max_arg.opportunity_type, hir_eqm_max_arg.k))

    print("Evolve Map")
    # print_evolve_map(state_evolvation, hashmap)
    # print_hash_map(hashmap)

    cur_state = system['env'].return_current_state()
    cur_state_object = system['emq'].return_object_of_state(cur_state)

    print("Intent Map: {}".format(intent_map_res))

    print('Length = {}, {}'.format(len(state_evolvation[cur_state_object.name]),len(state_evolvation)))
    print('K = {}'.format(K))
        # graph(state_evolvation, hashmap, cur_state_object.name)
    # except Exception as e:
    #     print("Main Exception")
    #     print(e)
