import os
import tempfile

def create_domain(types_list, predicates_list, action_list):
    name_domain = "domain.pddl"

    f = open(name_domain, "w+")

    f.write(" (define (domain recipe) \n" +
          "(:requirements \n" +
          " :strips \n" +
          " :negative-preconditions \n" +
          " :equality \n" +
          " :typing \n" +
          " :derived-predicates ) \n")


    f.write(" (:types ")

    #dish food - main ) " )

    for items in types_list:
        for item in types_list[items]:
            f.write(item)
            f.write(" ")

        if (len(types_list[items]) > 0):
            f.write(" - ")
        f.write(items)

    f.write(
    " ) \n (:predicates ")
    # "   (has_a ?s - dish ?x - food) \n " +
    # "   (collected ?x - food) \n " +
    # "   (submitted ?x - dish) \n " +
    # "   (collected_all ?x - dish) ) \n " )

    for items in predicates_list:
        f.write(" (")
        f.write(items)
        f.write(") \n ")

    f.write(
    " ) \n (:derived (collected_all ?s - dish) \n "+
    "    (forall (?x - food) \n "+
    "    (and \n "+
    "      (imply (has_a ?s ?x) (collected ?x)) \n "+
    "      (imply (and (not (has_a ?s ?x)) (collected ?x))  (not (collected ?x))) \n "+
    "    ) )  ) \n ")

    for each in action_list:
        each_action = action_list[each]
        f.write(
            "  (:action " + each_action.name + "\n "+
            "    :parameters" + each_action.parameter + "\n "+
            "    :precondition "+ each_action.precondition +  " \n "+
            "    :effect " + each_action.effect + " \n "+
            "  ) \n ")

    #final paranthesis
    f.write(
    " ) \n ")

    f.close()

    return name_domain



def create_problem(goal, objects, relationship_list, list_init):
    name_problem = "problem_%s.pddl" %goal

    f= open(name_problem,"w+")

    f.write("(define (problem recipe-" + goal + ") \n" +
    "  (:domain recipe) \n" +
    "  (:objects  \n" )

    for obj in objects:
        for item in objects[obj]:
            f.write(" %s - %s \n" %(item, obj))

    # "     soup - dish   \n" +
    # "     cake - dish   \n" +
    # "     water - food   \n" +
    # "     flour - food   \n" +
    # "      lentil - food  \n" +
    # "      chocolate - food  \n" +
    # "      sugar - food \n" +
    # "      salt - food  \n" +
    # "      pepper - food  \n" )

    f.write(
    " \n ) \n (:init   \n" )

    for items in relationship_list:
        f.write(" (")
        f.write(items)
        f.write(") \n ")

    #write init
    for event in list_init:
      f.write("( %s ) \n" %event)

    f.write( ")(:goal \n" ) #adding goal

    #add goal
    f.write("(submitted %s)" %goal)
    f.write (" ) ) ") #last paranthesis

    f.close()

    return name_problem
