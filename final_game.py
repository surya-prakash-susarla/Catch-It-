import pygame 
import threading
import time
import random
from class_based_opencv import opencv_module
import class_based_opencv
import sys

SIZE_X = SIZE_Y = 60
SCORE = 0 

# VARIABLE : class_based_opencv.sensitivity_gesture -- INT 
# EFFECT : Change this value to affect the sensitivity of direction identification based on pixel values moved.

# VARIABLE : class_based_opencv.display_window -- BOOL
# EFFECT : Change to display the opencv window currently showing the object being tracked 

# VARIABLE : class_based_opencv.list_length -- INT
# EFFECT : Contains the length of the points to be tracked for direction ( affects sensitivity ) 

game_image = pygame.image.load ( 'icon.png' )
game_image = pygame.transform.scale ( game_image , (30,30) )
food_image = pygame.image.load ( 'food.png' )
food_image = pygame.transform.scale ( food_image , (30,30) )

pygame.init()
pygame.display.set_caption ( "CATCH IT !!!" )
screen = pygame.display.set_mode ( (600,600) )

step = 5
direction_updates = { 'top' : (0,-step) , 'bottom' : (0,step) , 'right' : (step,  0 ) ,'left' : (-step, 0) }

QUIT = False

COLOR = ( 255 , 0 , 0 )

x = y =  40 

CLOCK = pygame.time.Clock()

input_from_opencv = prev_direction = direction = 'right'

opencv_class = opencv_module()
continuous_direction_thread = threading.Thread ( target = opencv_class.recognise_direction )
continuous_direction_thread.start()

food_x = food_y = -1 

def food_generator():
	while getattr ( threading.currentThread() , "do_run" , True ) :
		global screen , food_x , food_y 
		food_x = random.randint( 0 , 599 )
		food_y = random.randint( 0 , 599 )
		time.sleep ( 5 ) 
		

food_generator_thread = threading.Thread ( target = food_generator ) 

def reverse_direction ( value ) :
	if value == 'right':
		return 'left'
	if value == 'left':
		return 'right'
	return value

def get_direction_periodic ():
	while getattr ( threading.currentThread() , "do_run" , True ):
		global input_from_opencv
		input_from_opencv = reverse_direction ( class_based_opencv.direction_value )
		#input_from_opencv = class_based_opencv.direction_values
		#print ( " setting input_from_opencv to " , input_from_opencv )
		time.sleep(0.15)

input_periodic_thread = threading.Thread( target = get_direction_periodic )

def limit_boundaries ( x, y ) :
	if x > 599:
		x = 0
	if y > 599:
		y = 0
	if x < 0:
		x = 599
	if y < 0:
		y= 599
	return x,y

myfont = pygame.font.SysFont('Comic Sans MS', 15)
while not class_based_opencv.start_moving and not QUIT :
	textsurface = myfont.render('Please draw the frame around the object to be tracked for controlling the object', False, (255, 255, 255))
	screen.blit(textsurface,(0,30))
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			QUIT = True 
			continuous_direction_thread.do_run = False 
			class_based_opencv.quit = True
			
	pygame.display.update()
	
input_periodic_thread.start()
food_generator_thread.start()
QUIT = False
class_based_opencv.quit = False
	
while not QUIT: 

	one_time_per_clock = False

	# input event
	# remove while connecting to gesturing stuff
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			#print ( "QUITTING THE GAME ! " )
			QUIT = True
			input_periodic_thread.do_run = False
			continuous_direction_thread.do_run = False
			class_based_opencv.quit = True
			food_generator_thread.do_run = False
			sys.exit(0)
	
	#fill screen with black color background
	screen.fill( (0,0,0) )
	
	direction = input_from_opencv
	#print("FOLLOWING DIRECTION " , direction )
	
	if direction == 'NULL':
		direction = prev_direction
	else:
		prev_direction = direction
	
	#print ( "FINAL DIRECTION BEING FOLLOWED : " , direction )
	
	x = x + direction_updates[direction][0]
	y = y + direction_updates[direction][1]
	
	x , y = limit_boundaries ( x,  y ) 
	
	screen.blit ( food_image , (food_x , food_y ) )
	
	if x == food_x and y == food_y:
		SCORE = SCORE+1
	
	textsurface = myfont.render( 'SCORE : ' + str ( SCORE )  , False, (255, 255, 255))
	screen.blit(textsurface,(450,0))
	
	#pygame.draw.rect ( screen , COLOR , pygame.Rect ( x, y, SIZE_X , SIZE_Y ) )
	screen.blit ( game_image , (x,y) )
	
	pygame.display.flip()
	CLOCK.tick(60)