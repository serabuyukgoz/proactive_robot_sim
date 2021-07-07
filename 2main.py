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
    system['env'].add_sub_types('main', 'dish')
    system['env'].add_sub_types('main', 'food')
    system['env'].add_sub_types('main', 'weather')
    system['env'].add_sub_types('main', 'time')

    #adding user's action for intention recognition

    system['env'].add_action("Human", "(?d - dish)", "(collected_all ?d)", "(submitted ?d)", "submit")
    system['env'].add_action("Human", "(?x - food)", "(not(collected ?x))", "(collected ?x)", "collect")
    system['env'].add_action("Human", "(?x - food)", "(collected ?x)", "(not(collected ?x))", "leave")

    #added robot actions for equilibrium maintenance, all of robot's action is communicative

#    system['env'].add_action("Robot", "(?d - dish)", "(collected_all ?d)", "(submitted ?d)", "tell_submit")
#    system['env'].add_action("Robot", "(?x - food)", "(not(collected ?x))", "(collected ?x)", "tell_collect")
#    system['env'].add_action("Robot", "(?x - food)", "(collected ?x)", "(not(collected ?x))", "tell_leave")

    #added actions for free run, changes of concepts!
#    system['env'].add_action("Free", "(?wp - weather ?wn - weather)", " ( ) ", "(and (not(current_weather ?wp)) (current_weather ?wn))", "weather_change")
#    system['env'].add_action("Free", "(?tp - time ?tn - time)", "(after ?tp ?tn)", "(and (not(current_time ?tp)) (current_time ?tn))", "time_change")

    system['env'].add_predicate("collected_all ?d - dish")
    system['env'].add_predicate("submitted ?d - dish")
    system['env'].add_predicate("collected ?x - food")
    system['env'].add_predicate("needed ?s - dish ?x - food")
    system['env'].add_predicate("current_weather ?w - weather")
    system['env'].add_predicate("current_time ?t - time")
    system['env'].add_predicate("after ?t1 - time ?t2 - time")

    system['env'].add_goal('( submitted soup )')
    system['env'].add_goal('( submitted cake )')
    system['env'].add_goal('( submitted smoothie )')

    system['env'].add_object('dish')
    system['env'].add_sub_objects('dish', 'soup')
    system['env'].add_sub_objects('dish', 'cake')
    system['env'].add_sub_objects('dish', 'smoothie')
    system['env'].add_object('food')
    system['env'].add_sub_objects('food', 'water')
    system['env'].add_sub_objects('food', 'flour')
#    system['env'].add_sub_objects('food', 'lentil')
    system['env'].add_sub_objects('food', 'chocolate')
#    system['env'].add_sub_objects('food', 'sugar')
    system['env'].add_sub_objects('food', 'salt')
    # system['env'].add_sub_objects('food', 'pepper')
    # system['env'].add_sub_objects('food', 'milk')
    # system['env'].add_sub_objects('food', 'sprinkle')
    # system['env'].add_sub_objects('food', 'coco')
    # system['env'].add_object('weather')
    # system['env'].add_sub_objects('weather', 'rainy')
    # system['env'].add_sub_objects('weather', 'cloudy')
    # system['env'].add_object('time')
    # system['env'].add_sub_objects('time', 'morning')
    # system['env'].add_sub_objects('time', 'lunch')
    # system['env'].add_sub_objects('time', 'after_noon')
    # system['env'].add_sub_objects('time', 'evening')
    # system['env'].add_sub_objects('time', 'night')

    #relationship added
    system['env'].add_common_knowledge(" needed soup water " )
    system['env'].add_common_knowledge(" needed soup salt " )
#    system['env'].add_common_knowledge(" needed soup pepper " )
#    system['env'].add_common_knowledge(" needed soup lentil " )
    system['env'].add_common_knowledge(" needed cake flour " )
    system['env'].add_common_knowledge(" needed cake chocolate " )
#    system['env'].add_common_knowledge(" needed cake sugar " )
#    system['env'].add_common_knowledge(" needed cake water " )
#    system['env'].add_common_knowledge(" needed smoothie milk " )
    system['env'].add_common_knowledge(" needed smoothie water " )
#    system['env'].add_common_knowledge(" needed smoothie sprinkle " )
    system['env'].add_common_knowledge(" needed smoothie chocolate " )

    # system['env'].add_common_knowledge(" after morning lunch " )
    # system['env'].add_common_knowledge(" after lunch after_noon " )
    # system['env'].add_common_knowledge(" after after_noon evening " )
    # system['env'].add_common_knowledge(" after evening night " )
    # system['env'].add_common_knowledge(" after night morning " )

    #related to the state description -> it could have chage later
    # system['env'].add_state_change("(current_weather rainy)")
    # system['env'].add_state_change("(current_time morning)")

    #derived predicates_list
    derived = " \n (:derived (collected_all ?s - dish) \n (forall (?x - food) \n (and \n (imply (needed ?s ?x) (collected ?x)) \n (imply (and (not (needed ?s ?x)) (collected ?x))  (not (collected ?x))) \n ) )  ) \n "
    system['env'].add_derived(derived)



    #ALSO add what is undesired situations to define which state will be undesired!
    system['des'].add_situation('get_wet', ['(current_weather rainy)' , '(left house)'], 0.1)
    system['des'].add_situation('cake_spoiled', ['(submitted cake)'], 0.5)
    system['des'].add_situation('pepper_alergy', ['(collected pepper)'], 0.0)
    system['des'].add_situation('too_much_sugar', ['(collected chocolate)'], 0.5)

    domain_name, problem_name = system['env'].create_environment()

    return (domain_name, problem_name)

def free_run_creation(system):
    list_init = system['env'].return_current_state()
    defined_action = system['env'].create_action_list_map()
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
    cur_state = system['env'].return_current_state()
    #oppo = system['opo'].checkAllOpportunitues(des, act_robot)
    oppo = system['opo'].findOpportunity(cur_state, des, evolve_map, hashmap_state)

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

    #print_all(react, system)

    robot_said = system["nav"].select_action_to_play(selected_plan)
    #print(robot_said)

    #Situation change
    #print("action played -> collected chocolate")
    system['env'].add_state_change("(collected chocolate)")

    react = time.time()
    selected_plan = updateSituation(system)
    react = time.time() - react

    #print_all(react, system)

    robot_said = system["nav"].select_action_to_play(selected_plan)
    #print(robot_said)
