import os
import tempfile
import subprocess
import copy

import time

from src.environment import Environment
from src.decoderDatabase import DecodeDatabase
from src.planner import run_planning
from src.intention_recognition import Intention

from src.naive_proactivity import Naive

from print_strategy import print_all

# My game start from here
system = { }

def setClasses():
    env = Environment()
    rec = Intention()

    system["env"] = env
    system["recogniser"] = rec

    nav = Naive()
    system["nav"] = nav


def create_world_state(system):

    system['env'].add_type('main')
    system['env'].add_sub_types('main', 'dish')
    system['env'].add_sub_types('main', 'food')

    system['env'].add_action("Robot", "(?d - dish)", "(collected_all ?d)", "(submitted ?d)", "submit")
    system['env'].add_action("Robot", "(?x - food)", "(not(collected ?x))", "(collected ?x)", "collect")
    system['env'].add_action("Robot", "(?x - food)", "(collected ?x)", "(not(collected ?x))", "leave")

    system['env'].add_predicate("collected_all ?d - dish")
    system['env'].add_predicate("submitted ?d - dish")
    system['env'].add_predicate("collected ?x - food")
    system['env'].add_predicate("has_a ?s - dish ?x - food")

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

    #relationship added
    system['env'].add_common_knowledge(" has_a soup water " )
    system['env'].add_common_knowledge(" has_a soup salt " )
    system['env'].add_common_knowledge(" has_a soup pepper " )
    system['env'].add_common_knowledge(" has_a soup lentil " )
    system['env'].add_common_knowledge(" has_a cake flour " )
    system['env'].add_common_knowledge(" has_a cake chocolate " )
    system['env'].add_common_knowledge(" has_a cake sugar " )
    system['env'].add_common_knowledge(" has_a cake water " )
    system['env'].add_common_knowledge(" has_a smoothie milk " )
    system['env'].add_common_knowledge(" has_a smoothie water " )
    system['env'].add_common_knowledge(" has_a smoothie sprinkle " )
    system['env'].add_common_knowledge(" has_a smoothie coco " )

    domain_name, problem_name = system['env'].create_environment()
    return (domain_name, problem_name)

def updateSituation(system):
    domain_name, problem_name = system['env'].create_environment()
    list_of_goals = system['env'].return_goal_list()
    #intent + plan
    intent = system['recogniser'].create_recogniser(list_of_goals, domain_name, problem_name)
    print(intent)

    desire = system['recogniser'].desirability_detection(intent, len(list_of_goals))

    plan_list = system['recogniser'].return_map()
    evolve_map = system['env'].evolve_state(intent, plan_list, 8)
    #evolve_map = system['env'].evolve_state([], plan_list, 3)
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
    system['env'].add_state_change("collected pepper")

    react = time.time()
    selected_plan = updateSituation(system)
    react = time.time() - react

    print_all(react, system)

    robot_said = system["nav"].select_action_to_play(selected_plan)
    print(robot_said)

    #Situation change
    print("action played -> collected chocolate")
    system['env'].add_state_change("collected chocolate")

    react = time.time()
    selected_plan = updateSituation(system)
    react = time.time() - react

    print_all(react, system)

    robot_said = system["nav"].select_action_to_play(selected_plan)
    print(robot_said)
