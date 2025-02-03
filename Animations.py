from time import time
from includes.VisualConstants import *

class Animation():
	def __init__(self, canvas_object, animation_function, on_start_function,clean_up_function, duration, delay):
		self.duration = duration
		self.delay = delay
		self.update_function = animation_function
		self.clean_up_function = clean_up_function
		self.on_start_function = on_start_function

		self.canvas_object = canvas_object

		self.terminate = False

		self.start_time = time()
		self.first_frame = None
		self.last_time = time()
		self.current_time = time()
		self.time_remaning = duration

	def iterate(self):
		self.last_time = self.current_time
		self.current_time = time()
		if self.current_time -  self.start_time < self.delay: return False
		if not self.first_frame: 
			self.first_frame = time()
			if self.on_start_function: self.on_start_function(self)

		dt = self.current_time - self.last_time

		self.time_remaning = self.duration - (self.current_time - self.first_frame)

		is_done = self.update_function(dt)

		is_done = is_done or self.time_remaning <= 0

		if is_done:
			self.clean_up()

		return is_done

class LinearTranslation(Animation):
	def __init__(self, drawer, canvas_obj, start_coords, end_coords, duration, delay, on_start, on_complete):
		super().__init__(canvas_obj, self.move, on_start, self.clean_up, duration, delay)
		self.drawer = drawer
		self.start_coords = start_coords
		self.end_coords = end_coords
		self.delay = delay
		self.duration = duration
		self.coords = self.start_coords

		self.on_complete = on_complete

		self.speed_x = (self.end_coords[0] - self.start_coords[0])/ self.duration
		self.speed_y = (self.end_coords[1] - self.start_coords[1])/ self.duration 

	def move(self, dt):
		# print('update')
		self.coords = (self.coords[0] + self.speed_x * dt, self.coords[1] + self.speed_y * dt)
		self.drawer.move(self.canvas_object, self.speed_x * dt, self.speed_y * dt)
		x, y = self.coords
		margin = 15
		return (self.end_coords[0] - margin <= x <= self.end_coords[0] + margin) and \
			(self.end_coords[1] - margin <= y <= self.end_coords[1] + margin)

	def clean_up(self):
		self.drawer.coords(self.canvas_object, self.end_coords[0],self.end_coords[1])
		
		self.on_complete(self)