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

    system['env'].add_object('agent')
    system['env'].add_sub_objects('agent', 'user')
    # system['env'].add_sub_objects('agent', 'robot')
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

    evolve_map, hashmap_state, des_map = evolve_map_creation()
    system['emq'].set_env(evolve_map, hashmap_state)
    system['emq'].des.add_des_map(des_map)

    hashmap_state = system['emq'].return_state_hash_map()
    evolve_map = system['emq'].return_evolve_map()
    setDesirability(hashmap_state, des_map)

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

def evolve_map_creation():

    evolve_map = {}
    hash_map = {}
    des_map ={}
    bnf_map = {}

    evolve_map['S0'] = ['S1.0','S1.1']
    evolve_map['S1.0'] = ['S2.0'] #,'S2.x']
    evolve_map['S1.1'] = ['S1.0', 'S2.1'] #,'S2.y']
    evolve_map['S2.0'] = ['S3.0']
    # evolve_map['S2.x'] = []
    # evolve_map['S2.y'] = []
    evolve_map['S2.1'] = ['S3.1']
    evolve_map['S3.0'] = ['S4.0','S4.1']
    evolve_map['S3.1'] = ['S4.0','S4.1']
    evolve_map['S4.0'] = []
    evolve_map['S4.1'] = []

    hash_map['S0'] = ['(current_weather sunshine)', '(current_time morning)', '(breakfast user)']
    hash_map['S1.0'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(dishes_dirty)']
    hash_map['S1.1'] = ['(current_weather sunshine)', '(current_time morning)', '(dishes_dirty)']
    hash_map['S2.0'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)']

    hash_map['S2.x'] = ['(current_weather sunshine)', '(current_time morning)', '(book_reading user)']
    hash_map['S2.y'] = ['(current_weather sunshine)', '(current_time morning)', '(watch_tv user)']
    hash_map['S2.1'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user sugar)']
    hash_map['S3.0'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)']
    hash_map['S3.1'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user sugar)', '(gathered user tea)']

    hash_map['S4.0'] = ['(current_weather hail)', '(current_time noon)', '(outside user)']

    hash_map['S4.1'] = ['(current_weather rainy)', '(current_time noon)', '(outside user)']


    hash_map['S0.safe'] = ['(current_weather sunshine)', '(current_time morning)', '(breakfast user)', '(warned user)']
    hash_map['S1.0.safe'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(dishes_dirty)', '(warned user)']
    hash_map['S1.1.safe'] = ['(current_weather sunshine)', '(current_time morning)', '(dishes_dirty)', '(warned user)']
    hash_map['S2.0.safe'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(warned user)']

    hash_map['S2.x.safe'] = ['(current_weather sunshine)', '(current_time morning)', '(book_reading user)', '(warned user)']
    hash_map['S2.y.safe'] = ['(current_weather sunshine)', '(current_time morning)', '(watch_tv user)', '(warned user)']
    hash_map['S2.1.safe'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user sugar)', '(warned user)']
    hash_map['S3.0.safe'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)', '(warned user)']
    hash_map['S3.1.safe'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user sugar)', '(gathered user tea)', '(warned user)']

    hash_map['S0.cbp'] = ['(current_weather sunshine)', '(current_time morning)', '(breakfast user)' , '(gathered robot backpack)']
    hash_map['S0.cb'] = ['(current_weather sunshine)', '(current_time morning)', '(breakfast user)' , '(gathered robot book)']
    hash_map['S0.cr'] = ['(current_weather sunshine)', '(current_time morning)', '(breakfast user)' , '(gathered robot remote)']
    hash_map['S0.cwb'] = ['(current_weather sunshine)', '(current_time morning)', '(breakfast user)' , '(gathered robot water_bottle)']
    hash_map['S0.ct'] = ['(current_weather sunshine)', '(current_time morning)', '(breakfast user)' , '(gathered robot tea)']
    hash_map['S0.cc'] = ['(current_weather sunshine)', '(current_time morning)', '(breakfast user)' , '(gathered robot compass)']
    hash_map['S0.cs'] = ['(current_weather sunshine)', '(current_time morning)', '(breakfast user)' , '(gathered robot sugar)']
    hash_map['S0.ch'] = ['(current_weather sunshine)', '(current_time morning)', '(breakfast user)' , '(gathered robot hat)']
    hash_map['S0.cd'] = ['(current_weather sunshine)', '(current_time morning)', '(breakfast user)' , '(gathered robot dog)']
    hash_map['S0.o'] = ['(current_weather sunshine)', '(current_time morning)', '(breakfast user)' , '(outside user)']

    hash_map['S1.0.cwb'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(dishes_dirty)', '(gathered robot water_bottle)']
    hash_map['S1.0.ct'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(dishes_dirty)', '(gathered robot tea)']
    hash_map['S1.0.cc'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(dishes_dirty)', '(gathered robot compass)']
    hash_map['S1.0.cs'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(dishes_dirty)', '(gathered robot sugar)']
    hash_map['S1.0.dc'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)']
    hash_map['S1.0.cb'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(dishes_dirty)', '(gathered robot book)']
    hash_map['S1.0.cr'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(dishes_dirty)', '(gathered robot remote)']
    hash_map['S1.0.ch'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(dishes_dirty)', '(gathered robot hat)']
    hash_map['S1.0.cd'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(dishes_dirty)', '(gathered robot dog)']
    hash_map['S1.0.o'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(dishes_dirty)', '(outside user)']

    hash_map['S1.1.cbp'] = ['(current_weather sunshine)', '(current_time morning)', '(dishes_dirty)' , '(gathered robot backpack)']
    hash_map['S1.1.cb'] = ['(current_weather sunshine)', '(current_time morning)', '(dishes_dirty)' , '(gathered robot book)']
    hash_map['S1.1.cb'] = ['(current_weather sunshine)', '(current_time morning)', '(dishes_dirty)' , '(gathered robot remote)']
    hash_map['S1.1.cwb'] = ['(current_weather sunshine)', '(current_time morning)', '(dishes_dirty)', '(gathered robot water_bottle)']
    hash_map['S1.1.ct'] = ['(current_weather sunshine)', '(current_time morning)', '(dishes_dirty)', '(gathered robot tea)']
    hash_map['S1.1.cc'] = ['(current_weather sunshine)', '(current_time morning)', '(dishes_dirty)', '(gathered robot compass)']
    hash_map['S1.1.cs'] = ['(current_weather sunshine)', '(current_time morning)', '(dishes_dirty)', '(gathered robot sugar)']
    hash_map['S1.1.dc'] = ['(current_weather sunshine)', '(current_time morning)']
    hash_map['S1.1.ch'] = ['(current_weather sunshine)', '(current_time morning)', '(dishes_dirty)', '(gathered robot hat)']
    hash_map['S1.1.cd'] = ['(current_weather sunshine)', '(current_time morning)', '(dishes_dirty)', '(gathered robot dog)']

    hash_map['S2.0.cwb'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered robot water_bottle)']
    hash_map['S2.0.ct'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered robot tea)']
    hash_map['S2.0.cs'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered robot sugar)']
    hash_map['S2.0.cb'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered robot book)']
    hash_map['S2.0.cr'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered robot remote)']
    hash_map['S2.0.ch'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered robot hat)']
    hash_map['S2.0.cd'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered robot dog)']

    # hash_map['S2.x.cbp'] = ['(current_weather sunshine)', '(current_time morning)', '(book_reading user)', '(gathered robot backpack)']
    # hash_map['S2.x.cb'] = ['(current_weather sunshine)', '(current_time morning)', '(book_reading user)', '(gathered robot book)']
    # hash_map['S2.x.cr'] = ['(current_weather sunshine)', '(current_time morning)', '(book_reading user)', '(gathered robot remote)']
    # hash_map['S2.x.cwb'] = ['(current_weather sunshine)', '(current_time morning)', '(book_reading user)', '(gathered robot water_bottle)']
    # hash_map['S2.x.ct'] = ['(current_weather sunshine)', '(current_time morning)', '(book_reading user)', '(gathered robot tea)']
    # hash_map['S2.x.cc'] = ['(current_weather sunshine)', '(current_time morning)', '(book_reading user)', '(gathered robot compass)']
    # hash_map['S2.x.cs'] = ['(current_weather sunshine)', '(current_time morning)', '(book_reading user)', '(gathered robot sugar)']
    # hash_map['S2.x.o'] = ['(current_weather sunshine)', '(current_time morning)', '(book_reading user)', '(outside user)']
    # hash_map['S2.x.ch'] = ['(current_weather sunshine)', '(current_time morning)', '(book_reading user)', '(gathered robot hat)']
    # hash_map['S2.x.cd'] = ['(current_weather sunshine)', '(current_time morning)', '(book_reading user)', '(gathered robot dog)']
    #
    # hash_map['S2.y.cbp'] = ['(current_weather sunshine)', '(current_time morning)', '(watch_tv user)', '(gathered robot backpack)']
    # hash_map['S2.y.cb'] = ['(current_weather sunshine)', '(current_time morning)', '(watch_tv user)', '(gathered robot book)']
    # hash_map['S2.y.cr'] = ['(current_weather sunshine)', '(current_time morning)', '(watch_tv user)', '(gathered robot remote)']
    # hash_map['S2.y.cwb'] = ['(current_weather sunshine)', '(current_time morning)', '(watch_tv user)', '(gathered robot water_bottle)']
    # hash_map['S2.y.ct'] = ['(current_weather sunshine)', '(current_time morning)', '(watch_tv user)', '(gathered robot tea)']
    # hash_map['S2.y.cc'] = ['(current_weather sunshine)', '(current_time morning)', '(watch_tv user)', '(gathered robot compass)']
    # hash_map['S2.y.cs'] = ['(current_weather sunshine)', '(current_time morning)', '(watch_tv user)', '(gathered robot sugar)']
    # hash_map['S2.y.o'] = ['(current_weather sunshine)', '(current_time morning)', '(watch_tv user)', '(outside user)']
    # hash_map['S2.y.ch'] = ['(current_weather sunshine)', '(current_time morning)', '(watch_tv user)', '(gathered robot hat)']
    # hash_map['S2.y.cd'] = ['(current_weather sunshine)', '(current_time morning)', '(watch_tv user)', '(gathered robot dog)']

    hash_map['S2.1.cbp'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user sugar)', '(gathered robot backpack)']
    hash_map['S2.1.cwb'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user sugar)', '(gathered robot water_bottle)']
    hash_map['S2.1.ct'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user sugar)', '(gathered robot tea)']
    hash_map['S2.1.cc'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user sugar)', '(gathered robot compass)']
    hash_map['S2.1.o'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user sugar)', '(outside user)']
    hash_map['S2.1.cb'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user sugar)', '(gathered robot book)']
    hash_map['S2.1.cr'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user sugar)', '(gathered robot remote)']
    hash_map['S2.1.ch'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user sugar)', '(gathered robot hat)']
    hash_map['S2.1.cd'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user sugar)', '(gathered robot dog)']

    hash_map['S3.0.ct'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)', '(gathered robot tea)']
    hash_map['S3.0.cs'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)', '(gathered robot sugar)']
    hash_map['S3.0.o'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)', '(outside user)']
    hash_map['S3.0.cb'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)', '(gathered robot book)']
    hash_map['S3.0.cr'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)', '(gathered robot remote)']
    hash_map['S3.0.ch'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)', '(gathered robot hat)']
    hash_map['S3.0.cd'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user backpack)', '(gathered user compass)', '(gathered user water_bottle)', '(gathered robot dog)']


    hash_map['S3.1.cbp'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user sugar)', '(gathered user tea)', '(gathered robot backpack)']
    hash_map['S3.1.cwb'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user sugar)', '(gathered user tea)', '(gathered robot water_bottle)']
    hash_map['S3.1.cc'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user sugar)', '(gathered user tea)', '(gathered robot compass)']
    hash_map['S3.1.o'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user sugar)', '(gathered user tea)', '(outside user)']
    hash_map['S3.1.cb'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user sugar)', '(gathered user tea)', '(gathered robot book)']
    hash_map['S3.1.cr'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user sugar)', '(gathered user tea)', '(gathered robot remote)']
    hash_map['S3.1.ch'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user sugar)', '(gathered user tea)', '(gathered robot hat)']
    hash_map['S3.1.cd'] = ['(current_weather sunshine)', '(current_time morning)', '(gathered user sugar)', '(gathered user tea)', '(gathered robot dog)']

    hash_map['S4.0'] = ['(current_weather hail)', '(current_time noon)', '(outside user)']
    hash_map['S4.0.safe'] = ['(current_weather hail)', '(current_time noon)', '(warned user)']
    hash_map['S4.0.cbp'] = ['(current_weather hail)', '(current_time noon)', '(outside user)', '(gathered robot backpack)']
    hash_map['S4.0.cwb'] = ['(current_weather hail)', '(current_time noon)', '(outside user)', '(gathered robot water_bottle)']
    hash_map['S4.0.ct'] = ['(current_weather hail)', '(current_time noon)', '(outside user)', '(gathered robot tea)']
    hash_map['S4.0.cc'] = ['(current_weather hail)', '(current_time noon)', '(outside user)', '(gathered robot compass)']
    hash_map['S4.0.cs'] = ['(current_weather hail)', '(current_time noon)', '(outside user)', '(gathered robot sugar)']
    hash_map['S4.0.cb'] = ['(current_weather hail)', '(current_time noon)', '(outside user)', '(gathered robot book)']
    hash_map['S4.0.cr'] = ['(current_weather hail)', '(current_time noon)', '(outside user)', '(gathered robot remote)']
    hash_map['S4.0.ch'] = ['(current_weather hail)', '(current_time noon)', '(outside user)', '(gathered robot hat)']
    hash_map['S4.0.cd'] = ['(current_weather hail)', '(current_time noon)', '(outside user)', '(gathered robot dog)']

    hash_map['S4.1'] = ['(current_weather rainy)', '(current_time noon)', '(outside user)']
    hash_map['S4.1.safe'] = ['(current_weather rainy)', '(current_time noon)', '(warned user)']
    hash_map['S4.1.cbp'] = ['(current_weather rainy)', '(current_time noon)', '(outside user)', '(gathered robot backpack)']
    hash_map['S4.1.cwb'] = ['(current_weather rainy)', '(current_time noon)', '(outside user)', '(gathered robot water_bottle)']
    hash_map['S4.1.ct'] = ['(current_weather rainy)', '(current_time noon)', '(outside user)', '(gathered robot tea)']
    hash_map['S4.1.cc'] = ['(current_weather rainy)', '(current_time noon)', '(outside user)', '(gathered robot compass)']
    hash_map['S4.1.cs'] = ['(current_weather rainy)', '(current_time noon)', '(outside user)', '(gathered robot sugar)']
    hash_map['S4.1.cb'] = ['(current_weather rainy)', '(current_time noon)', '(outside user)', '(gathered robot book)']
    hash_map['S4.1.cr'] = ['(current_weather rainy)', '(current_time noon)', '(outside user)', '(gathered robot remote)']
    hash_map['S4.1.ch'] = ['(current_weather rainy)', '(current_time noon)', '(outside user)', '(gathered robot hat)']
    hash_map['S4.1.cd'] = ['(current_weather rainy)', '(current_time noon)', '(outside user)', '(gathered robot dog)']


    des_map['S0'] = 1.0
    des_map['S1.0'] = 0.6
    des_map['S1.1'] = 0.6
    des_map['S2.0'] = 1.0
    des_map['S2.x'] = 1.0
    des_map['S2.y'] = 1.0
    des_map['S2.1'] = 1.0
    des_map['S3.0'] = 1.0
    des_map['S3.1'] = 1.0
    des_map['S4.0'] = 0
    des_map['S4.1'] = 0.4

    des_map['S0.cb'] = 0.01
    des_map['S0.cbp'] = 0.01
    des_map['S0.cr'] = 0.01
    des_map['S0.cwb'] = 0.01
    des_map['S0.ct'] = 0.01
    des_map['S0.cc'] = 0.01
    des_map['S0.cs'] = 0.01
    des_map['S0.ch'] = 0.01
    des_map['S0.cd'] = 0.01
    des_map['S0.o'] = 0.01

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

    return evolve_map, hash_map, des_map

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

    system['pla'].set_path('/Users/serabuyukgoz/Code/humanAi/planner')
    system['pla'].set_python_version('3')
    #
    # system['pla'].set_path('~/planner/fast_downward/downward')
    # system['pla'].set_python_version('3.6')
    '''
      Other search methods also could be use depend on the complexity of problem
      Such as; "astar(lmcut())" , "astar(ipdb())" ...
    '''
    system['pla'].set_search_method("astar(add())")

    domain_name, problem_name = create_world_state(system)

    # S0
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


    react = time.time()
    desirability_map, opp_emq, opp_hir, state_evolvation, hashmap, reaction_time, intent_map_res, K = updateSituation(system)
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
