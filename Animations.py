from time import time
from includes.VisualConstants import *

class Animation():
	def __init__(self, canvas_object, animation_function, clean_up_function, duration, delay):
		self.duration = duration
		self.delay = delay
		self.update_function = animation_function
		self.clean_up_function = clean_up_function

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
		if not self.first_frame: self.first_frame = time()

		dt = self.current_time - self.last_time

		self.time_remaning = self.duration - (self.current_time - self.first_frame)

		is_done = self.update_function(dt)

		is_done = is_done or self.time_remaning <= 0

		if is_done:
			self.clean_up()

		return is_done


class DealCardAnimation(Animation):
	def __init__(self, drawer, image, card_face, start_coords, end_coords, duration, delay, seat_index):
		super().__init__(image, self.move, self.clean_up, duration, delay)
		self.drawer = drawer
		self.start_coords = start_coords
		self.end_coords = end_coords
		self.delay = delay
		self.duration = duration
		self.card_face = card_face
		self.coords = self.start_coords
		self.seat_index = seat_index

		self.speed_x = (self.end_coords[0] - self.start_coords[0])/ self.duration
		self.speed_y = (self.end_coords[1] - self.start_coords[1])/ self.duration 

	def move(self, dt):
		self.drawer.itemconfigure(self.canvas_object,state='normal')
		self.coords = (self.coords[0] + self.speed_x * dt, self.coords[1] + self.speed_y * dt)
		self.drawer.coords(self.canvas_object, self.coords[0], self.coords[1])
		self.drawer.tag_raise(self.canvas_object)
		x, y = self.coords
		margin = 15
		return (self.end_coords[0] - margin <= x <= self.end_coords[0] + margin) and \
			(self.end_coords[1] - margin <= y <= self.end_coords[1] + margin)

	def clean_up(self):
		self.drawer.cards_to_deal[self.seat_index] -= 1
		self.drawer.coords(self.canvas_object, self.end_coords[0],self.end_coords[1])

		if self.card_face:
			self.drawer.itemconfigure(self.canvas_object, image=self.card_face)

		del self.card_face
		del self

class DiscardCardAnimation(Animation):
	def __init__(self, drawer, image, start_coords, end_coords, duration, delay, on_complete):
		super().__init__(image, self.move, self.clean_up, duration, delay)
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
		print('update')
		self.coords = (self.coords[0] + self.speed_x * dt, self.coords[1] + self.speed_y * dt)
		self.drawer.coords(self.canvas_object, self.coords[0], self.coords[1])
		self.drawer.tag_raise(self.canvas_object)
		x, y = self.coords
		margin = 15
		return (self.end_coords[0] - margin <= x <= self.end_coords[0] + margin) and \
			(self.end_coords[1] - margin <= y <= self.end_coords[1] + margin)

	def clean_up(self):
		self.drawer.coords(self.canvas_object, self.end_coords[0],self.end_coords[1])
		
		self.on_complete(self)