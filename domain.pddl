 (define (domain recipe) 
(:requirements 
 :strips 
 :negative-preconditions 
 :equality 
 :typing 
 :derived-predicates ) 
 (:types obj agent weather time  - main 
  ) 
 (:constants 
 sunshine hail rainy cloudy  - weather 
 morning noon evening  - time 
 compass backpack walking_stick dog water_bottle tea milk chocolate flour sugar  - obj 
  ) 
 (:predicates  (collected ?u - agent ?x - objects) 
  (outside ?u - agent) 
  (current_weather ?w - weather) 
  (current_time ?t - time) 
  (after ?t1 - time ?t2 - time) 
  (breakfast ?u - agent) 
  (weather_dealt) 
  (dishes_dirty) 
 )  (:action leave_home
     :parameters(?u - agent)
     :precondition (not(outside ?u)) 
     :effect (outside ?u) 
   ) 
   (:action clean_dishes
     :parameters(?u - agent)
     :precondition (and (dishes_dirty) (not(outside ?u)) ) 
     :effect (not(dishes_dirty)) 
   ) 
   (:action collect
     :parameters(?u - agent ?x - obj)
     :precondition (and (not(collected ?u ?x)) (not(outside ?u)) ) 
     :effect (collected ?u ?x) 
   ) 
   (:action leave
     :parameters(?u - agent ?x - obj)
     :precondition (and (collected ?u ?x) (not(outside ?u)) ) 
     :effect (not(collected ?u ?x)) 
   ) 
  ) 
 