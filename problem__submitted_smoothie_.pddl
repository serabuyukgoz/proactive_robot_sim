(define (problem recipe-ex1) 
  (:domain recipe) 
  (:objects  
 soup - dish 
 cake - dish 
 smoothie - dish 
 water - food 
 flour - food 
 lentil - food 
 chocolate - food 
 sugar - food 
 salt - food 
 pepper - food 
 milk - food 
 sprinkle - food 
 coco - food 
 
 ) 
 (:init   
 ( has_a soup water ) 
  ( has_a soup salt ) 
  ( has_a soup pepper ) 
  ( has_a soup lentil ) 
  ( has_a cake flour ) 
  ( has_a cake chocolate ) 
  ( has_a cake sugar ) 
  ( has_a cake water ) 
  ( has_a smoothie milk ) 
  ( has_a smoothie water ) 
  ( has_a smoothie sprinkle ) 
  ( has_a smoothie coco ) 
 ( collected pepper ) 
( collected chocolate ) 
)(:goal 
( submitted smoothie ) ) ) 