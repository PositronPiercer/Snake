import cv2
import numpy as np
import time

import threading
from pynput import keyboard
from pynput.keyboard import Key




def snake_update():
	global arena
	global arena_dimensions
	global snake
	global position
	global snake_color
	global snake_size
	global snake_width
	global snake_head_size
	global snake_head_color
	global score
	global snake_has_eaten_food
	#itr =1
	color_selector=0
	gap_length=10
	
	draw_color=(0,0,0)
	snake_has_eaten_food=False
	game_over=False
	while not game_over:
			#itr=itr+1
		   # print(snake)
			
			arena= np.zeros(arena_dimensions,np.uint8) # refreshing arena
			#draw a boundary

			tail_end=(snake[-1][0],snake[-1][1])
			snake_itr=0
			for index in range(0,snake_size): # updating the arena
				points=snake[index]
				i=points[0]
				j=points[1]
				direct=points[2]
				
				if position[i][j] != -1:  # get the break points
					direct=position[i][j]
				#print(direct)
				#direction logic
				if direct==0:
					i=i-1   #left
				elif direct==1:
					i=i+1   #right
				elif direct==2:
					j=j-1   #up
				elif direct==3:
					j=j+1   #down

				snake_itr=snake_itr+1
				
				if snake_has_gone_out_of_boundary(i,j):
					game_over=True

				if snake_itr<snake_head_size:
					draw_color=snake_head_color
					#print('painting head')
				else:
					if snake_itr%gap_length==0:
						color_selector=1-color_selector
					draw_color=snake_color[color_selector]
				cv2.rectangle(arena,(i-snake_width,j-snake_width),(i+snake_width,j+snake_width),draw_color,-1)

				
				snake[index]=(i,j,direct)

			position[tail_end]=-1 # removing direction constraint from snake's tail end
			food_spawner()

			obj=snake_has_encountered()

			if obj=='food':
				#print('food eaten')
				snake_has_eaten_food=True
				score+=1
				print('Score : '+str(score))
				increase_snake_length()
			elif obj=='a_snake':
				print('snake bitten')
				game_over=True
				# snake has eaten a snake. Game over


		   # print('displaying')
			cv2.imshow("Snake",arena)
			if cv2.waitKey(1)==27:
				cv2.destroyAllWindows()
				break
				#time.sleep(0.05)
	print('Game Over')
	print('Press esc to quit')

def snake_has_gone_out_of_boundary(i,j):
	global arena_dimensions
	
	if (i<0 or i>=arena_dimensions[0]) or (j<0 or j>=arena_dimensions[1]):
		return True
	else:
		return False
def increase_snake_length():
	global snake
	global snake_size
	delta_length=10
	
	direct=snake[-1][2]

	x_itr=0
	y_itr=0

	if direct==0:
		#snake was moving left
		x_itr=1
	elif direct==1:
		#snake was moving right
		x_itr=-1
	elif direct==2:
		#snake was moving  up
		y_itr=1
	elif direct==3:
		#snake was moving down
		y_itr=-1
	else:
		print('Damn! Where did that come from!!')

	for i in range(0,delta_length):
		snake.append((snake[-1][0]+x_itr,snake[-1][1]+y_itr,direct))
		snake_size+=1





def snake_has_encountered():
	global snake
	global snake_size
	global snake_width
	global arena
	global food_position
	global food_radius
	
	#checking for self intersection
	snake_head_coor=np.array([snake[0][0],snake[0][1]])
	for index in range(snake_width+10,snake_size):
		coor=np.array([snake[index][0],snake[index][1]])
		distance=np.linalg.norm(snake_head_coor-coor)
		if distance<snake_width:
			return 'a_snake'
			
	#checking if the snake has eaten food
	distance=np.linalg.norm(food_position-snake_head_coor)
	if distance<food_radius:
		return 'food'
	
	return 'nothing'




def on_press(key):
	global snake
	global arena
   # print(snake[-1])
	try:
		if key==Key.up and not(snake[0][2] == 3): #if the snake is moving down, it cannot directly move up
			position[snake[0][0]][snake[0][1]]=2
			
			#print('move up')
		elif key==Key.down and not(snake[0][2] == 2):
			position[snake[0][0]][snake[0][1]]=3
			
			#print('move down')
		elif key==Key.left and not(snake[0][2] == 1):
			position[snake[0][0]][snake[0][1]]=0
		   
			#print('move left')
		elif key==Key.right and not(snake[0][2] == 0):
			position[snake[0][0]][snake[0][1]]=1
		   
			#print('move right')
	except AttributeError:
			print('Hmmm there is some problem.')


def on_release(key):
	if key == keyboard.Key.esc:
		#stop listner
		return False

def snake_intersecting_food(food_position):
	global arena
	if arena[food_position][0]==0 and arena[food_position][1]==0 and arena[food_position][2]==0 : #food spawned at an empty location
		return False    #would be better if we checked not just a point but an area around it which is clear
	else:
		
		return True



def food_spawner():
	import random
	global food_position
	global snake_has_eaten_food
	global arena_dimensions
	
	global arena
	global food_color
	global food_radius

	if snake_has_eaten_food:
		food_position=(random.randint(10,arena_dimensions[0]-50),random.randint(10,arena_dimensions[1]-50))
		while snake_intersecting_food(food_position):
			food_position=(random.randint(10,arena_dimensions[0]-50),random.randint(10,arena_dimensions[1]-50))
		snake_has_eaten_food=False
		
		
	#draw the food
	cv2.circle(arena,(food_position[0],food_position[1]), food_radius, food_color, -1)
	#print('food spawned at '+str(food_position))



if __name__ =="__main__":
	arena_dimensions=(600,600,3)
	arena= np.zeros(arena_dimensions,np.uint8)  #play area
	position= np.zeros((arena_dimensions[0],arena_dimensions[1]),np.int8) #direction pointers
	for a in range(0,arena_dimensions[0]-1):
		for b in range(0,arena_dimensions[0]-1):
			position[a][b]=-1

	food_color=(0,0,255)
	snake_color=[(255,255,255),(255,0,0)]
	snake_size=50
	snake_width=3
	starting_offset=10
	snake_starting=snake_size+starting_offset
	snake_head_size=10
	snake_head_color=(0,255,0)
	score=0
	
	food_position=np.array([200,10])
	food_radius=5
	snake_has_eaten_food=False

	snake=[(snake_starting,starting_offset,1)]   # (x,y,direction)
	for j in range(snake_starting-1,starting_offset,-1):
		snake.append((j,10,1))
	#print(len(snake))
	# thread to update snake
	snake_update_thread=threading.Thread(target=snake_update)
	snake_update_thread.start()

	#food_thread=threading.Thread(target=food_spawner(snake_has_eaten_food))
	#food_thread.start()


	with keyboard.Listener(
		on_press=on_press,
		on_release=on_release
	) as listener:
		listener.join()
		snake_update_thread.join()
		#food_thread.join()



        




