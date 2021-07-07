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

from print_strategy import print_all, print_des

# My game start from here
system = { }

def setClasses():
    env = Environment()
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
    system['env'].add_sub_types('main', 'user')
    system['env'].add_sub_types('main', 'weather')
    system['env'].add_sub_types('main', 'time')

    #adding user's action for intention recognition

    system['env'].add_action("Human", "(?u - user)", "(and (not(outside ?u)) (weather_dealt))", "(outside ?u)", "leave_home")
    system['env'].add_action("Human", " ( ) ", "(dishes_dirty)", "(not(dishes_dirty))", "clean_dishes")
    system['env'].add_action("Human", "(?u - user)", "(and (collected backpack) (collected compass) (outside ?u))", "(hiking ?u)", "go_hiking")
    system['env'].add_action("Human", "(?u - user)", "(and (collected walking_stick) (collected dog) (outside ?u))", "(watching_tv ?u)", "go_promenade")
    system['env'].add_action("Human", "(?u - user)", "(and (not (outside ?u)) )", "(watching_tv ?u)", "watch_tv")
    system['env'].add_action("Human", "(?u - user)", "(and (not (outside ?u)) (collected book))", "(reading_book ?u)", "read_book")
    system['env'].add_action("Human", "(?x - obj)", "(not(collected ?x))", "(collected ?x)", "collect")
    system['env'].add_action("Human", "(?x - obj)", "(collected ?x)", "(not(collected ?x))", "leave")
    #added robot actions for equilibrium maintenance, all of robot's action is communicative

    system['env'].add_action("Robot", "(?d - dish)", "(collected_all ?d)", "(submitted ?d)", "tell_clean_dishes")
    system['env'].add_action("Robot", "(?x - obj)", "(not(collected ?x))", "(collected ?x)", "tell_gather")
    system['env'].add_action("Robot", "(?u - user)", "(collected ?x)", "(not(outside ?u))", "warn_weather")

    #added actions for free run, changes of concepts!
#    system['env'].add_action("Free", "(?wp - weather ?wn - weather)", "(current_weather ?wp)", "(and (not (current_weather ?wp)) (current_weather ?wn))", "weather_change")
#    system['env'].add_action("Free", "(?tp - time ?tn - time)", "(after ?tp ?tn)", "(and (not (current_time ?tp)) (current_time ?tn))", "time_change")
    system['env'].add_action("Free", "(?u - user)", "(breakfast ?u)", "(dishes_dirty)", "had_breakfast")

    system['env'].add_predicate("collected ?x - objects")
    system['env'].add_predicate("outside ?u - user")
    system['env'].add_predicate("current_weather ?w - weather")
    system['env'].add_predicate("current_time ?t - time")
    system['env'].add_predicate("after ?t1 - time ?t2 - time")

    system['env'].add_predicate("hiking ?u - user")
    system['env'].add_predicate("promenade ?u - user")
    system['env'].add_predicate("watching_tv ?u - user")
    system['env'].add_predicate("reading_book ?u - user")
    system['env'].add_predicate("breakfast ?u - user")

    system['env'].add_predicate("weather_dealt")
    system['env'].add_predicate("dishes_dirty")

    # system['env'].add_goal('( hiking ?u - user)')
    # system['env'].add_goal('( promenade ?u - user)')
    # system['env'].add_goal('( reading_book ?u - user)')
    # system['env'].add_goal('( watching_tv ?u - user)')

    system['env'].add_goal('(hiking ali)')
    system['env'].add_goal('(promenade ali)')
    system['env'].add_goal('(reading_book ali)')
    system['env'].add_goal('(watching_tv ali)')

    system['env'].add_object('user')
    system['env'].add_sub_objects('user', 'ali')

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
    system['env'].add_state_change("(breakfast ali)")

    #derived predicates_list
    derived = " \n (:derived (weather_dealt) \n (or \n (and (current_weather sunshine) (collected hat)) \n (and (current_weather rainy) (collected umbrella)) \n  )  ) \n "
    system['env'].add_derived(derived)



    #ALSO add what is undesired situations to define which state will be undesired!
    system['des'].add_situation('get_wet', ['(current_weather rainy)' , '(outside ?u - user)'], 0.5)
    system['des'].add_situation('get_hurt', ['(current_weather hail)' , '(outside ?u - user)'], 1.0)
    system['des'].add_situation('dirt_dishes', ['(dishes_dirty)'], 0.2)

    domain_name, problem_name = system['env'].create_environment()

    return (domain_name, problem_name)

def free_run_creation(system):
    list_init_name, list_init = system['env'].return_current_state()
    unvoluntary_action_list = system['env'].return_unvoluntary_action_list()
    defined_action = system['env'].create_action_list_map(unvoluntary_action_list)
    system['env'].create_evolve_map(list_init, defined_action)
    maps = system['env'].return_state_map()
    hashmap_state = system['env'].return_state_hash_map()
    #history_map = system['env'].return_state_evolution()
    print('---------------------------------------------')
    print('State Evolvation adjacency List-> {}'.format(maps))
    print('------------------------------------------------')
    print('Name of State Hash Map {}'.format(hashmap_state))
    print('---------------------------------------------')


def updateSituation(system):
    domain_name, problem_name = system['env'].create_environment()
    list_of_goals = system['env'].return_goal_list()
    #intent + plan
    intent = system['recogniser'].create_recogniser(list_of_goals, domain_name, problem_name)
    #print(intent)

    desire = system['recogniser'].desirability_detection(intent, len(list_of_goals))

    plan_list = system['recogniser'].return_map()

    '''
        we do not need to create the map over and over again,
        the general map will never changed!
        Since known all actions and combinations already registered
        Which is an adjacency list
    '''

    evolve_map = system['env'].return_state_map()
    hashmap_state = system['env'].return_state_hash_map()
    des = system['des'].desirabilityFunction(evolve_map, hashmap_state)
    print('______________________')
    print('Desirabilily Calculation \n {}'.format(des))
    act_robot = system['env'].return_robot_action_list()
    cur_state_name, cur_state = system['env'].return_current_state()
    K = 2 #look up strategy
    oppo = system['opo'].findOpportunity(evolve_map, des, cur_state_name, act_robot, K)

    return plan_list


if __name__ =='__main__':
    print("Hello World!")
    setClasses()

    domain_name, problem_name = create_world_state(system)
    free_run_creation(system) #for equilibrium maintenance, create the map of the all possible state
    #for every change in Situation
    react = time.time()
    selected_plan = updateSituation(system)
    react = time.time() - react

    #print_all(react, system)

    robot_said = system["nav"].select_action_to_play(selected_plan)
    #print(robot_said)


    #Situation change
    #print("action played -> collected pepper")
    #system['env'].add_state_change("(collected pepper)")
    system['env'].add_state_change("(collected water)")

    react = time.time()
    selected_plan = updateSituation(system)
    react = time.time() - react
