import os
import tempfile
import subprocess
import copy

import time

from src.environment import Environment
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
    system['env'].add_type('object')
    system['env'].add_sub_types('main' , 'object')
    system['env'].add_sub_types('object', 'toy')
    system['env'].add_sub_types('object', 'battery')
    system['env'].add_sub_types('main', 'place')
    system['env'].add_sub_types('object', 'agent')
    system['env'].add_sub_types('main', 'time')
    system['env'].add_sub_types('main', 'weather')

    #adding user's action for intention recognition

    system['env'].add_action("Human", "(?from - place ?to - place ?h - agent)", "(and (at ?h ?from) (orient_left ?from ?to) (not (obstacle ?to)) )", "(and (not (at ?h ?from)) (at ?h ?to) )", "move-left")
    system['env'].add_action("Human", "(?from - place ?to - place ?h - agent)", "(and (at ?h ?from) (orient_right ?from ?to) (not (obstacle ?to)) )", "(and (not (at ?h ?from)) (at ?h ?to) )", "move-right")
    system['env'].add_action("Human", "(?from - place ?to - place ?h - agent)", "(and (at ?h ?from) (orient_up ?from ?to) (not (obstacle ?to)) )", "(and (not (at ?h ?from)) (at ?h ?to) )", "move-up")
    system['env'].add_action("Human", "(?from - place ?to - place ?h - agent)", "(and (at ?h ?from) (orient_down ?from ?to) (not (obstacle ?to)) )", "(and (not (at ?h ?from)) (at ?h ?to) )", "move-down")

    system['env'].add_action("Human", "(?h - agent ?p - place ?x - toy)", "(and (not(gathered ?x)) (at ?h ?p) (placed ?x ?p))", "(and (gathered ?x) (not (at ?x ?p)))", "collect")
    system['env'].add_action("Human", "(?x - object)", "(gathered ?x)", "(not(gathered ?x))", "dismiss")

    #added robot actions for equilibrium maintenance, all of robot's action is communicative


    #added high-level state actions done by Human
    #system['env'].add_action("system", "(?x - food)", "(not(gathered ?x))", "(gathered ?x)", "make_dough" )

    system['env'].add_predicate("current_weather ?w - weather")
    system['env'].add_predicate("current_time ?t - time")
    system['env'].add_predicate("at ?h - human ?p - place")
    system['env'].add_predicate("placed ?t - toy ?p - place")
    system['env'].add_predicate("gathered ?o - object")
    system['env'].add_predicate("obstacle ?p - place")
    system['env'].add_predicate("orient_left ?p1 - place ?p2 - place")
    system['env'].add_predicate("orient_right ?p1 - place ?p2 - place")
    system['env'].add_predicate("orient_up ?p1 - place ?p2 - place")
    system['env'].add_predicate("orient_down ?p1 - place ?p2 - place")
#    system['env'].add_predicate("is_goal ?o - object")

    system['env'].add_goal('( gathered bear )')
    system['env'].add_goal('( gathered goal )')

    system['env'].add_object('place')
    system['env'].add_sub_objects('place', 'p0')
    system['env'].add_sub_objects('place', 'p1')
    system['env'].add_sub_objects('place', 'p2')
    system['env'].add_sub_objects('place', 'p3')
    system['env'].add_sub_objects('place', 'p4')
    system['env'].add_sub_objects('place', 'p5')
    system['env'].add_sub_objects('place', 'p6')
    system['env'].add_sub_objects('place', 'p7')
    system['env'].add_sub_objects('place', 'p8')
    system['env'].add_sub_objects('place', 'p9')
    system['env'].add_sub_objects('place', 'p10')
    system['env'].add_sub_objects('place', 'p11')
    system['env'].add_sub_objects('place', 'p12')
    system['env'].add_sub_objects('place', 'p13')
    system['env'].add_sub_objects('place', 'p14')
    system['env'].add_sub_objects('place', 'p15')
    system['env'].add_object('agent')
    system['env'].add_sub_objects('agent', 'human')
    system['env'].add_object('toy')
    system['env'].add_sub_objects('toy', 'bear')
    system['env'].add_sub_objects('toy', 'gold')
    system['env'].add_sub_objects('toy', 'train')
    system['env'].add_object('battery')
    system['env'].add_sub_objects('battery', 'm')
    system['env'].add_sub_objects('battery', 'mm')
    system['env'].add_object('weather')
    system['env'].add_sub_objects('weather', 'rainy')
    system['env'].add_sub_objects('weather', 'cloudy')
    system['env'].add_object('time')
    system['env'].add_sub_objects('time', 'morning')
    system['env'].add_sub_objects('time', 'lunch')
    system['env'].add_sub_objects('time', 'after_noon')
    system['env'].add_sub_objects('time', 'evening')
    system['env'].add_sub_objects('time', 'night')

    #relationship added
    system['env'].add_common_knowledge(" orient_up p0 p0 " )
    system['env'].add_common_knowledge(" orient_right p0 p1 " )
    system['env'].add_common_knowledge(" orient_down p0 p4 " )
    system['env'].add_common_knowledge(" orient_left p0 p0 " )

    system['env'].add_common_knowledge(" orient_up p1 p1 " )
    system['env'].add_common_knowledge(" orient_right p1 p2 " )
    system['env'].add_common_knowledge(" orient_down p1 p5 " )
    system['env'].add_common_knowledge(" orient_left p1 p0 " )

    system['env'].add_common_knowledge(" orient_up p2 p2 " )
    system['env'].add_common_knowledge(" orient_right p2 p3 " )
    system['env'].add_common_knowledge(" orient_down p2 p6 " )
    system['env'].add_common_knowledge(" orient_left p2 p1 " )

    system['env'].add_common_knowledge(" orient_up p3 p3 " )
    system['env'].add_common_knowledge(" orient_right p3 p3 " )
    system['env'].add_common_knowledge(" orient_down p3 p7 " )
    system['env'].add_common_knowledge(" orient_left p3 p2 " )

    system['env'].add_common_knowledge(" orient_up p4 p0 " )
    system['env'].add_common_knowledge(" orient_right p4 p5 " )
    system['env'].add_common_knowledge(" orient_down p4 p8 " )
    system['env'].add_common_knowledge(" orient_left p4 p4 " )

    system['env'].add_common_knowledge(" orient_up p5 p1 " )
    system['env'].add_common_knowledge(" orient_right p5 p6 " )
    system['env'].add_common_knowledge(" orient_down p5 p9 " )
    system['env'].add_common_knowledge(" orient_left p5 p4 " )

    system['env'].add_common_knowledge(" orient_up p6 p2 " )
    system['env'].add_common_knowledge(" orient_right p6 p7 " )
    system['env'].add_common_knowledge(" orient_down p6 p10 " )
    system['env'].add_common_knowledge(" orient_left p6 p5 " )

    system['env'].add_common_knowledge(" orient_up p7 p3 " )
    system['env'].add_common_knowledge(" orient_right p7 p7 " )
    system['env'].add_common_knowledge(" orient_down p7 p11 " )
    system['env'].add_common_knowledge(" orient_left p7 p6 " )

    system['env'].add_common_knowledge(" orient_up p8 p4 " )
    system['env'].add_common_knowledge(" orient_right p8 p9 " )
    system['env'].add_common_knowledge(" orient_down p8 p12 " )
    system['env'].add_common_knowledge(" orient_left p8 p8 " )

    system['env'].add_common_knowledge(" orient_up p9 p5 " )
    system['env'].add_common_knowledge(" orient_right p9 p10 " )
    system['env'].add_common_knowledge(" orient_down p9 p13 " )
    system['env'].add_common_knowledge(" orient_left p9 p8 " )

    system['env'].add_common_knowledge(" orient_up p10 p6 " )
    system['env'].add_common_knowledge(" orient_right p10 p11 " )
    system['env'].add_common_knowledge(" orient_down p10 p14 " )
    system['env'].add_common_knowledge(" orient_left p10 p9 " )

    system['env'].add_common_knowledge(" orient_up p11 p7 " )
    system['env'].add_common_knowledge(" orient_right p11 p11 " )
    system['env'].add_common_knowledge(" orient_down p11 p15 " )
    system['env'].add_common_knowledge(" orient_left p11 p10 " )

    system['env'].add_common_knowledge(" orient_up p12 p8 " )
    system['env'].add_common_knowledge(" orient_right p12 p13 " )
    system['env'].add_common_knowledge(" orient_down p12 p12 " )
    system['env'].add_common_knowledge(" orient_left p12 p12 " )

    system['env'].add_common_knowledge(" orient_up p13 p9 " )
    system['env'].add_common_knowledge(" orient_right p13 p14 " )
    system['env'].add_common_knowledge(" orient_down p13 p13 " )
    system['env'].add_common_knowledge(" orient_left p13 p12 " )

    system['env'].add_common_knowledge(" orient_up p14 p10 " )
    system['env'].add_common_knowledge(" orient_right p14 p15 " )
    system['env'].add_common_knowledge(" orient_down p14 p14 " )
    system['env'].add_common_knowledge(" orient_left p14 p13 " )

    system['env'].add_common_knowledge(" orient_up p15 p11 " )
    system['env'].add_common_knowledge(" orient_right p15 p15 " )
    system['env'].add_common_knowledge(" orient_down p15 p15 " )
    system['env'].add_common_knowledge(" orient_left p15 p14 " )

    #related to the state description -> it could have chage later
    system['env'].add_state_change("current_weather rainy")
    system['env'].add_state_change("current_time morning")

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
    print("action played -> gathered pepper")
    system['env'].add_state_change("gathered pepper")

    react = time.time()
    selected_plan = updateSituation(system)
    react = time.time() - react

    print_all(react, system)

    robot_said = system["nav"].select_action_to_play(selected_plan)
    print(robot_said)

    #Situation change
    print("action played -> gathered chocolate")
    system['env'].add_state_change("gathered chocolate")

    react = time.time()
    selected_plan = updateSituation(system)
    react = time.time() - react

    print_all(react, system)

    robot_said = system["nav"].select_action_to_play(selected_plan)
    print(robot_said)
