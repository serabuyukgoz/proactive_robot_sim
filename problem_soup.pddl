(define (problem recipe-soup) 
  (:domain recipe) 
  (:objects  
     soup - dish   
     cake - dish   
     water - food   
     flour - food   
      lentil - food  
      chocolate - food  
      sugar - food 
      salt - food  
      pepper - food  
 
 ) 
 (:init   
   (has_a soup water)  
  (has_a soup salt)  
  (has_a soup pepper)  
  (has_a soup lentil)  
  (has_a cake flour)  
  (has_a cake chocolate)  
  (has_a cake sugar)  
  (has_a cake water)  
( collected pepper ) 
( collected chocolate ) 
)(:goal 
(submitted soup) ) ) 