(define (problem recipe-ex1) 
  (:domain recipe) 
  (:objects  
 user - agent 
 
 ) 
 (:init   
 ( after morning lunch ) 
  ( after lunch after_noon ) 
  ( after after_noon evening ) 
  ( after evening night ) 
  ( after night morning ) 
 (current_weather sunshine) 
 (current_time morning) 
 (breakfast user) 
 )(:goal 
(and (not (outside user)) (collected user water_bottle) (collected user sugar) (collected user tea) (collected user milk))  ) ) 