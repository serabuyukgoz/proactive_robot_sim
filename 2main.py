import os
import tempfile
import subprocess
import copy

import time

from src.environment import Environment
from src.planner import run_planning
from src.intention_recognition import Intention
from src.desireability import CalculateDesireability

from src.naive_proactivity import Naive

from print_strategy import print_all, print_des

# My game start from here
system = { }

def setClasses():
    env = Environment()
    rec = Intention()
    des = CalculateDesireability()

    system["env"] = env
    system["recogniser"] = rec
    system["des"] = des

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

    system['env'].add_action("Robot", "(?d - dish)", "(collected_all ?d)", "(submitted ?d)", "tell_submit")
    system['env'].add_action("Robot", "(?x - food)", "(not(collected ?x))", "(collected ?x)", "tell_collect")
    system['env'].add_action("Robot", "(?x - food)", "(collected ?x)", "(not(collected ?x))", "tell_leave")

    system['env'].add_predicate("collected_all ?d - dish")
    system['env'].add_predicate("submitted ?d - dish")
    system['env'].add_predicate("collected ?x - food")
    system['env'].add_predicate("needed ?s - dish ?x - food")
    system['env'].add_predicate("current_weather ?w - weather")
    system['env'].add_predicate("current_time ?t - time")

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
    system['env'].add_sub_objects('food', 'lentil')
    system['env'].add_sub_objects('food', 'chocolate')
    system['env'].add_sub_objects('food', 'sugar')
    system['env'].add_sub_objects('food', 'salt')
    system['env'].add_sub_objects('food', 'pepper')
    system['env'].add_sub_objects('food', 'milk')
    system['env'].add_sub_objects('food', 'sprinkle')
    system['env'].add_sub_objects('food', 'coco')
    system['env'].add_object('weather')
    system['env'].add_sub_objects('weather', 'rainy')
    system['env'].add_sub_objects('weather', 'cloudy')
    system['env'].add_object('time')
    system['env'].add_sub_objects('weather', 'morning')
    system['env'].add_sub_objects('weather', 'lunch')
    system['env'].add_sub_objects('weather', 'after_noon')
    system['env'].add_sub_objects('weather', 'evening')
    system['env'].add_sub_objects('weather', 'night')

    #relationship added
    system['env'].add_common_knowledge(" needed soup water " )
    system['env'].add_common_knowledge(" needed soup salt " )
    system['env'].add_common_knowledge(" needed soup pepper " )
    system['env'].add_common_knowledge(" needed soup lentil " )
    system['env'].add_common_knowledge(" needed cake flour " )
    system['env'].add_common_knowledge(" needed cake chocolate " )
    system['env'].add_common_knowledge(" needed cake sugar " )
    system['env'].add_common_knowledge(" needed cake water " )
    system['env'].add_common_knowledge(" needed smoothie milk " )
    system['env'].add_common_knowledge(" needed smoothie water " )
    system['env'].add_common_knowledge(" needed smoothie sprinkle " )
    system['env'].add_common_knowledge(" needed smoothie coco " )

    #related to the state description -> it could have chage later
    system['env'].add_state_change("(current_weather rainy)")
    system['env'].add_state_change("(current_time morning)")

    #derived predicates_list
    derived = " \n (:derived (collected_all ?s - dish) \n (forall (?x - food) \n (and \n (imply (needed ?s ?x) (collected ?x)) \n (imply (and (not (needed ?s ?x)) (collected ?x))  (not (collected ?x))) \n ) )  ) \n "
    system['env'].add_derived(derived)

    domain_name, problem_name = system['env'].create_environment()

    #ALSO add what is undesired situations to define which state will be undesired!
    system['des'].add_situation('get_wet', ['(current_weather rainy)' , '(left house)'], 0.1)
    system['des'].add_situation('cake_spoiled', ['(submitted cake)'], 0.5)
    system['des'].add_situation('pepper_alergy', ['(collected pepper)'], 0.0)
    system['des'].add_situation('too_much_sugar', ['(collected chocolate)'], 0.5)


    return (domain_name, problem_name)

def updateSituation(system):
    domain_name, problem_name = system['env'].create_environment()
    list_of_goals = system['env'].return_goal_list()
    #intent + plan
    intent = system['recogniser'].create_recogniser(list_of_goals, domain_name, problem_name)
    print(intent)

    desire = system['recogniser'].desirability_detection(intent, len(list_of_goals))

    plan_list = system['recogniser'].return_map()
    evolve_map = system['env'].evolve_state(intent, plan_list, 8) #if you listed K value long enough then ot will work!
    #evolve_map = system['env'].evolve_state([], plan_list, 3)
    des = system['des'].desirabilityFunction([], evolve_map)
    print("Desirability Function")
    print_des(des)
    return plan_list


if __name__ =='__main__':
    print("Hello World!")
    setClasses()

    domain_name, problem_name = create_world_state(system)

    #for every change in Situation
    react = time.time()
    selected_plan = updateSituation(system)
    react = time.time() - react

    print_all(react, system)

    robot_said = system["nav"].select_action_to_play(selected_plan)
    print(robot_said)


    #Situation change
    print("action played -> collected pepper")
    system['env'].add_state_change("(collected pepper)")

    react = time.time()
    selected_plan = updateSituation(system)
    react = time.time() - react

    print_all(react, system)

    robot_said = system["nav"].select_action_to_play(selected_plan)
    print(robot_said)

    #Situation change
    print("action played -> collected chocolate")
    system['env'].add_state_change("(collected chocolate)")

    react = time.time()
    selected_plan = updateSituation(system)
    react = time.time() - react

    print_all(react, system)

    robot_said = system["nav"].select_action_to_play(selected_plan)
    print(robot_said)
