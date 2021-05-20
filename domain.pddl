 (define (domain recipe) 
(:requirements 
 :strips 
 :negative-preconditions 
 :equality 
 :typing 
 :derived-predicates ) 
 (:types dish food  - main ) 
 (:predicates  (collected_all ?d - dish) 
  (submitted ?d - dish) 
  (collected ?x - food) 
  (has_a ?s - dish ?x - food) 
  ) 
 (:derived (collected_all ?s - dish) 
     (forall (?x - food) 
     (and 
       (imply (has_a ?s ?x) (collected ?x)) 
       (imply (and (not (has_a ?s ?x)) (collected ?x))  (not (collected ?x))) 
     ) )  ) 
   (:action submit
     :parameters(?d - dish)
     :precondition (collected_all ?d) 
     :effect (submitted ?d) 
   ) 
   (:action collect
     :parameters(?x - food)
     :precondition (not(collected ?x)) 
     :effect (collected ?x) 
   ) 
   (:action leave
     :parameters(?x - food)
     :precondition (collected ?x) 
     :effect (not(collected ?x)) 
   ) 
  ) 
 