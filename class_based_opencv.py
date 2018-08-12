import cv2
import numpy as np
from scipy.interpolate import spline 
import threading

direction_value = 'NULL'
start_moving = False
quit = False
sensitivity_gesture = 18
display_window = True
list_length = 10 

class queue_list:
	values = []
	length = -1 
	
	def __init__ ( self, len ):
		self.length = len
	
	def insert ( self , value ):
		if len(self.values) < self.length:
			self.values.append(value)
		else:
			new_list = []
			new_list.append(value)
			self.values = self.values[1:] + new_list 
		
	def get_max_min ( self ):
		minimum = self.values[0]
		maximum = self.values[len(self.values)-1]
		return (minimum,  maximum)
	
	def get_direction ( self ):
		global sensitivity_gesture
		DIRECTION_VALUES = [ 'right' , 'left' , 'bottom' , 'top' ]
		y_change = x_change = 0
		for i in range(len(self.values)-1,0,-1):
				y_change = self.values[i][1] - self.values[i-1][1]
				x_change = self.values[i][0] - self.values[i-1][0]
		
		temp_x = x_change
		temp_y = y_change
		
		if temp_x < 0:
			temp_x = 0 - temp_x
		if temp_y < 0:
			temp_y = 0 - temp_y
		
		if temp_x < sensitivity_gesture and temp_y < sensitivity_gesture :
			return 'NULL'
		
		if temp_x > temp_y:
			#DISPLACEMENT OF X IS GREATER THAN Y
			if x_change > 0:
				return DIRECTION_VALUES[0]
			else:
				return DIRECTION_VALUES[1]
		else:
			#DISPLACEMENT OF Y IS GREATER THAN X
			if y_change > 0:
				return DIRECTION_VALUES[2]
			else:
				return DIRECTION_VALUES[3]
		return 'NULL'
		
class opencv_module:
	
	def __init__(self):
		pass
	
	def recognise_direction ( self ) :
		global direction_value , start_moving , quit , display_window , list_length
		cam = cv2.VideoCapture(0)		
		DIRECTION_VALUES = [ 'right' , 'left' , 'bottom' , 'top' ]
		height , width = 480 , 640
		temp_frame = None 

		while cam.isOpened() and getattr(threading.currentThread(),"do_run",True) and not quit :
			_ , frame = cam.read()

			if frame.all() != None and temp_frame == None : 
				temp_frame = None
			
			cv2.imshow ("FRAME" , frame )
			
			hsv = cv2.cvtColor ( frame , cv2.COLOR_BGR2HSV ) 

			key_value = cv2.waitKey(10)
			
			if key_value == 32:
				box_values = cv2.selectROI ( frame ) 

				roi = hsv [ box_values[1] : box_values[1] + box_values[3] , box_values[0] : box_values[0] + box_values[2] ]
				
				cv2.destroyAllWindows()
				break

		if temp_frame != None:
			frame_x = temp_frame.shape[0]
			frame_y = temp_frame.shape[1]

		min_h , max_h = 180 , 0 
		min_s , max_s = 255 , 0 
		min_v , max_v = 255 , 0 
		
		for i in roi : 
			for j in i : 
				if j[0] < min_h :
					min_h = j[0]
				if j[0] > max_h :
					max_h = j[0]
				if j[1] < min_s :
					min_s = j[1]
				if j[1] > max_s :
					max_s = j[1]
				if j[2] < min_v :
					min_v = j[2]
				if j[2] > max_v :
					max_v = j[2]

		lower_value = np.array ( [min_h , min_s , min_v ] )
		upper_value = np.array ( [max_h , max_s , max_v ] )

		line_queue = queue_list ( list_length )

		#collecting points for plotting line / curve
		#points_queue = queue_list ( 400 )
		
		start_moving = True
		
		while cam.isOpened() and getattr(threading.currentThread(),"do_run",True) and not quit :
		
			_ , frame = cam.read () 
			
			hsv = cv2.cvtColor ( frame , cv2.COLOR_BGR2HSV )
			
			mask = cv2.inRange ( hsv , lower_value , upper_value )

			result = cv2.bitwise_and ( frame , frame , mask = mask )

			gray_value = cv2.cvtColor ( result , cv2.COLOR_BGR2GRAY )
			
			_ , contours , _ = cv2.findContours ( mask , cv2.RETR_TREE , cv2.CHAIN_APPROX_NONE )
			
			#cv2.drawContours ( frame , contours , -1 , ( 0 ,255, 0) , 3 )
			
			##print ( "updated and completed drawing the contours " )
			
			max_area = -1 
			final_contour = contours
						
			for i in contours:
				area = cv2.contourArea ( i )
				
				if area > max_area : 
					max_area = area 
					final_contour = i
				
			cv2.drawContours ( frame , final_contour , -1 , ( 0,255,0 ) , 3)
			if max_area > 0 :
				##print ( "contour found with max_area"  , max_area ) 
				m = cv2.moments(final_contour)
				##print ( "completed calculating the moments of the countour ")
				if m["m00"] == 0:
					break
				cX = int(m["m10"]/m["m00"])
				cY = int(m["m01"]/m["m00"])
				line_queue.insert ( (cX,cY) )
				##print ( "the points are " , cX , " " , cY )
				DIRECTION = line_queue.get_direction()
				#cv2.putText ( frame , DIRECTION , ( 0,50) , cv2.FONT_HERSHEY_SIMPLEX , 2, (255,255,255) , 2, cv2.LINE_AA )
				#cv2.circle(frame, (cX, cY), 7, (255, 255, 255), -1)
				#cv2.putText(frame, "center", (cX - 20, cY - 20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
				direction_value = DIRECTION
				cv2.putText ( gray_value, DIRECTION , ( 0,50) , cv2.FONT_HERSHEY_SIMPLEX , 2, (255,255,255) , 2, cv2.LINE_AA )
				cv2.circle(gray_value, (cX, cY), 7, (255, 255, 255), -1)
				cv2.putText( gray_value, "center", (cX - 20, cY - 20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
					
			if display_window:
				cv2.imshow ( "contour result " , gray_value )
			
			esc_character = cv2.waitKey(10)
			
			if esc_character == 27:
				break
			
			#print ( "continuing the while loop" )
				
		cv2.destroyWindow ( 'contour result' )
		
## DEBUG CODE FOR TESTING THE FUNCTIONING OF THE CLASSES
#temp = opencv_module()
#temp.recognise_direction()