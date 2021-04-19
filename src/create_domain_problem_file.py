import os
import tempfile

def create_domain():
    name_domain = "domain.pddl"

    f = open(name_domain, "w+")

    f.write(" (define (domain recipe) \n" +
          "(:requirements \n" +
          " :strips \n" +
          " :negative-preconditions \n" +
          " :equality \n" +
          " :typing \n" +
          " :derived-predicates ) \n")


    f.write(" (:types  dish food - main ) " +

    "  (:predicates (has_a ?s - dish ?x - food) \n " +
    "   (collected ?x - food) \n " +
    "   (submitted ?x - dish) \n " +
    "  (collected_all ?x - dish) ) \n "+



    " (:derived (collected_all ?s - dish) \n "+
    "    (forall (?x - food) \n "+
    "    (and \n "+
    "      (imply (has_a ?s ?x) (collected ?x)) \n "+
    "      (imply (and (not (has_a ?s ?x)) (collected ?x))  (not (collected ?x))) \n "+
    "    ) )  ) \n "+


    "  (:action collect \n "+
    "    :parameters (?x - food) \n "+
    "    :precondition(not(collected ?x)) \n "+
    "    :effect(collected ?x) \n "+
    "  ) \n "+

    "  (:action leave \n "+
    "    :parameters (?x - food) \n "+
    "    :precondition(collected ?x) \n "+
    "    :effect(not(collected ?x)) \n "+
    "  ) \n "+

    "  (:action submit \n "+
    "    :parameters(?d - dish) \n "+
    "    :precondition (collected_all ?d) \n "+
    "    :effect(submitted ?d) \n "+
    "  ) \n "+
    " ) \n ")

    f.close()

    return name_domain

def create_problem(goal, list_init):
    name_problem = "problem_%s.pddl" %goal

    f= open(name_problem,"w+")

    f.write("(define (problem recipe-" + goal + ") \n" +
    "  (:domain recipe) \n" +
    "  (:objects  \n" +
    "     soup - dish   \n" +
    "     cake - dish   \n" +
    "     water - food   \n" +
    "     flour - food   \n" +
    "      lentil - food  \n" +
    "      chocolate - food  \n" +
    "      sugar - food \n" +
    "      salt - food  \n" +
    "      pepper - food  \n" +
    " \n ) \n (:init   \n" +
    "   (has_a soup water)  \n" +
    "  (has_a soup salt)  \n" +
    "  (has_a soup pepper)  \n" +
    "  (has_a soup lentil)  \n" +
    "  (has_a cake flour)  \n" +
    "  (has_a cake chocolate)  \n" +
    "  (has_a cake sugar)  \n" +
    "  (has_a cake water)  \n" )

    #write init
    for event in list_init:
      f.write("( %s ) \n" %event)

    f.write( ")(:goal \n" ) #adding goal

    #add goal
    f.write("(submitted %s)" %goal)
    f.write (" ) ) ") #last paranthesis

    f.close()

    return name_problem
