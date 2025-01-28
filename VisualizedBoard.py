from tkinter import *
from PIL import Image,ImageTk

from math import sin, cos, radians, sqrt
from time import sleep, time

from Cards import Deck, find_card_path
import sys

from Client import Player

from StatusCodes import *

W,H = (1200, 600)
SEATS = 6
DEAL_SPEED = 0.3
DELAY = 0.25

scale = 170/120
CARD_W = 100
CARD_H = int(CARD_W*scale)


FELT_GREEN = '#277714'
ACENT_GREEN = '#348C2E'
YELLOW = '#F2C94C'
BLACK = '#000000'
GOLD='#D1A15B'
BLUE='#3385B1'
BROWN='#5C3A21'
PURPLE='#4B0082'
WHITE='#FFFFFF'

CHIP_COLORS = ["#F44336", "#FF9800", "#FFEB3B", "#4CAF50", "#2196F3", "#9C27B0", "#00BCD4", "#FF5722", "#3F51B5", "#8E44AD"]
CHIP_FG = [WHITE, BLACK, BLACK, WHITE, WHITE, WHITE, BLACK, BLACK, WHITE, WHITE]
CHIP_DENOMINATIONS = [25, 50, 100, 250, 500, 1000, 2500, 10000]



class App(Tk):
	def __init__(self, name, starting_money):
		super().__init__()
		screen_width = self.winfo_screenwidth()
		screen_height = self.winfo_screenheight()

		user_action_height = 100

		try:
			self.player_client = Player(name,starting_money)
		except Exception as e:
			print("No Server Running / Cannot Connect")
			raise e
			exit(1)

		self.action_queue = []
		self.ready_to_quit = False
		self.round_going = True
		self.animations = []

		self.title("BlackJack")
		# self.attributes('-topmost', True) 
		self.resizable(0,0)
		self.geometry("%sx%s+%s+%s"%(W,H+user_action_height,(screen_width // 2) - (W // 2),(screen_height // 2) - ((H+user_action_height) // 2)))

		self.table_can = Table(self, width=W, height=H, bd=0, highlightthickness=0, bg=FELT_GREEN)
		self.table_can.pack()

		self.user_actions = UserActions(self, width=W, height=user_action_height, bg=BROWN)
		self.user_actions.pack()
		self.user_actions.pack_propagate(0)

		self.bind('q', lambda e: self.do_action(LEAVE))

		

	def render_updates(self, content):

		if self.round_going and (content['turn_index'] == None):
			self.table_can.reset()
			self.round_going = False
			print('reset')
			 # this is between rounds
			 # make it so it doesnt reset over and over and over
			 
		else:
			self.round_going = content['turn_index'] != None
			
			self.table_can.render_updates(content)

			personal_money = content['players'][content['index']]['money']
			self.user_actions.render_updates(personal_money)

	def start(self):
		while not self.ready_to_quit:
			self.update_idletasks()
			self.update()

			if len(self.action_queue) != 0:
				action = self.action_queue.pop(0)

				status, content = self.player_client.take_action(action,None)
				if status == CLOSED:
					break


				# take action

			# refresh / process updates
			status, content = self.player_client.take_action(VIEW,None)
			if status == SUCCESS:
				self.render_updates(content)


			for animation_i in range(len(self.animations) - 1, -1, -1):
				status = self.animations[animation_i].iterate()
				if status:
					self.animations.pop(animation_i)


			sleep(0.01)

		print("CLOSING")

	def do_action(self, action):
		self.action_queue.append(action)

class UserActions(Frame):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.bet_mods = []

		self.bet_amount = 0

		third = self['width']*0.33

		self.money_frame = Frame(self,height=self['height'],bg=self['bg'])
		self.money_frame.pack(side=LEFT)

		self.bet_frame = Frame(self, height=self['height'],bg=self['bg'])
		self.bet_frame.pack(side=LEFT)


		self.action_frame = Frame(self,height=self['height'],bg=self['bg'])
		self.action_frame.pack(side=RIGHT,expand=True,fill='both')
		# self.action_frame.pack_propagate(0)

		font_size = 18
		bet_inc_size = 24


		self.hit_btn = Button(self.action_frame, text='Hit', command=self.hit,highlightbackground=self.action_frame['bg'], bg=self.action_frame['bg'], font=('Arial',font_size))
		self.hit_btn.pack(side="left", fill="y")

		self.stand_btn = Button(self.action_frame, text='Stand', command=self.stand,highlightbackground=self.action_frame['bg'], bg=self.action_frame['bg'], font=('Arial',font_size))
		self.stand_btn.pack(side="left", fill="y")

		self.double_btn = Button(self.action_frame, text='Double', command=self.double,highlightbackground=self.action_frame['bg'], bg=self.action_frame['bg'], font=('Arial',font_size))
		self.double_btn.pack(side="left", fill="y")

		for chip_value, chip_color in zip(CHIP_DENOMINATIONS[:7], CHIP_COLORS):
			editor = BetModifier(chip_value,self.update_bet_label, self.bet_frame,width=55,height=self.bet_frame['height'],bg=chip_color)
			editor.pack(side=LEFT)
			editor.pack_propagate(0)
			self.bet_mods.append(editor)


		self.bank_label = Label(self.money_frame,text='',font=('Arial',32),width=10,bg=self.money_frame['bg'],fg=WHITE)
		self.bank_label.pack()

		self.bet_view = Label(self.bet_frame,text='$0',font=('Arial',32),width=10,bg=self.bet_frame['bg'],fg=WHITE)
		self.bet_view.pack(side=LEFT)

		self.make_bet = Button(self.bet_frame, text='Place Bet', command=self.bet,highlightbackground=self.bet_frame['bg'], bg=self.bet_frame['bg'], font=('Arial',font_size))
		self.make_bet.pack(side="left", fill="y", expand=True)


		self.update_bet_label()

		game_flow = Frame(self.action_frame, bg=self.action_frame['bg'],height=self.action_frame['height'])
		game_flow.pack(side=LEFT, fill="both", expand=True)

		self.ready_btn = Button(game_flow, text='Ready Up', command=self.ready,highlightbackground=game_flow['bg'], bg=game_flow['bg'], font=('Arial',font_size))
		self.ready_btn.pack(side=TOP, fill="both", expand=True)

		self.end_btn = Button(game_flow, text='Clear', command=self.end,highlightbackground=game_flow['bg'], bg=game_flow['bg'], font=('Arial',font_size))
		self.end_btn.pack(side=TOP, fill="both", expand=True)

	def change_bet(self, amount):
		self.bet_amount += amount
		self.update_bet_label()

	def update_bet_label(self):
		total_bet = 0
		for editor in self.bet_mods:
			total_bet += editor.get_total()

		self.bet_amount = total_bet


		self.bet_view.config(text="${:,}".format(self.bet_amount))

	def hit(self):
		print("hitting")
		self.master.do_action(HIT)

	def start(self):
		print("start")
		self.master.do_action(START)

	def end(self):
		print("ending")
		self.master.do_action(END)

	def stand(self):
		print("stading")
		self.master.do_action(STAND)

	def ready(self):
		print("ready/unready")
		self.master.do_action(READY)

	def double(self):
		print("double")
		self.master.do_action(DOUBLE)

	def bet(self):
		print('betting',self.bet_amount)
		self.master.do_action('bet %d'%self.bet_amount)

	def render_updates(self,personal_money):
		if personal_money:
			self.bank_label.config(text="${:,}".format(personal_money))

class BetModifier(Frame):
	def __init__(self,delta, update_func, *args,**kwargs):
		super().__init__(*args,**kwargs)

		self.delta = delta

		self.chip_count = 0
		self.on_update = update_func

		self.font_size = 16

		self.inc = Button(self, text='+%d'%self.delta, command=lambda : self.edit_chips(1),highlightbackground=self['bg'], bg=self['bg'], font=('Arial',self.font_size))
		self.dec = Button(self, text='-%d'%self.delta, command=lambda : self.edit_chips(-1),highlightbackground=self['bg'], bg=self['bg'], font=('Arial',self.font_size))
		self.label = Label(self,text='0',width=3,height=1,font=('Arial', self.font_size))

		self.inc.pack(side=TOP,fill='both',expand=True)
		self.label.pack(side=TOP,fill='both',expand=True,padx=4)
		self.dec.pack(side=TOP,fill='both',expand=True)


	def edit_chips(self, count):
		if self.chip_count + count < 0: return

		self.chip_count += count

		self.label.config(text='%d'%self.chip_count)

		self.on_update()

	def get_total(self):
		return self.delta * self.chip_count

class Table(Canvas):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.seats = []
		self.players = []
		self.dealer = Dealer(self, W/2, 110, 600,180)
		self.deck_location = self.dealer.deck_location


		self.cards_to_deal = [0] * (SEATS + 1)

		player_space = W / (SEATS + 1)
		y = 425
		x = player_space
		scale = 1.3
		width = CARD_W*scale
		height = CARD_H*scale

		for i in range(SEATS):
			seat = Seat(self, i, x ,y, width, height)
			self.seats.append(seat)
			x += player_space

	def render_updates(self, content):
		for i, player in enumerate(content['players']):
			seat = self.seats[player['seat']]
			seat.render_updates(player, i, i == content['index'], i == content['turn_index'])

		self.dealer.render_updates(content)

		self.tag_lower('table')

	def done_dealing(self, seat=None):
		if not seat: return sum(self.cards_to_deal) == 0
		return self.cards_to_deal[seat] == 0


	def reset(self):
		self.dealer.reset()
		for seat in self.seats:
			seat.reset()


class Chip():
	def __init__(self, drawer_manager, x, y, r):
		self.drawer = drawer_manager
		self.x = x 
		self.y = y 
		self.r = r

		self.chip = self.drawer.create_oval(x-r,y-r,x+r,y+r,fill=WHITE,outline=BLACK,width=2,state='hidden')
		self.value_tag = self.drawer.create_text(x,y, text='', fill=BLACK,font=('Arial',16))

	def reset(self):
		self.render_updates(0)

	def render_updates(self,amount):
		chip_bg = WHITE
		chip_fg = BLACK
		state = 'hidden'
		bet_text = ''
		if amount > 0:
			chip_index = -1
			for i in range(len(CHIP_DENOMINATIONS)-1, 0, -1):
				if amount - CHIP_DENOMINATIONS[i] >= 0:
					chip_index = i
					break

			if chip_index != -1:
				chip_bg = CHIP_COLORS[chip_index]
				chip_fg = CHIP_FG[chip_index]
				state = 'normal'
				bet_text = "${:,}".format(amount)

		self.drawer.itemconfigure(self.chip, state=state, fill=chip_bg)

		self.drawer.itemconfigure(self.value_tag, text=bet_text,fill=chip_fg)
		self.drawer.tag_raise(self.value_tag)

class Animation():
	def __init__(self, animation_function, clean_up_function, duration, delay):
		self.duration = duration
		self.delay = delay
		self.update_function = animation_function
		self.clean_up_function = clean_up_function

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


class Seat():
	def __init__(self, drawer_manager, seat_index, x, y, w, h):
		self.drawer = drawer_manager
		self.seat_index = seat_index
		self.hand = Hand(self.drawer, seat_index, x - (CARD_W /2),y  - (CARD_H /2), (0, 25))

		self.hands = []

		bet_radius = w*0.25

		betx,bety = (x - (w/2) + bet_radius,y-(1.7*h/2))

		chip_r = 0.85*bet_radius
		

		self.turn_highlight = self.drawer.create_rectangle(x-(w/1.65),y-(h/1.65),x+(w/1.65),y+(h/1.65), fill=FELT_GREEN, outline=FELT_GREEN, width=1,tags='table')
		self.card_area = self.drawer.create_rectangle(x-(w/2),y-(h/2),x+(w/2),y+(h/2), fill=FELT_GREEN, outline=YELLOW, width=3,tags='table')
		self.bet_area = self.drawer.create_oval(betx-bet_radius, bety-bet_radius,betx+bet_radius, bety+bet_radius, fill=FELT_GREEN, outline=YELLOW, width=3,tags='table')
		self.name_tag = self.drawer.create_text(x,y-(h/2)-10, text='', fill=BLACK,font=('Arial',18,'bold'))
		self.sum_hint_tag = self.drawer.create_text(x+bet_radius, bety, text='', fill=GOLD, font=('Arial',18))
		self.seat_notification = SmartLabel(self.drawer, x, y, ('Arial',48, 'bold'), 'red', 'black')
		self.ready_tag = SmartLabel(self.drawer, x, y, ('Arial',24,'bold'), 'lime')		


		self.bet_chips = []
		self.earnings_chips = []

		locations = []
		dist = chip_r * 1.75
		for i in range(0,360,int(360/7)):
			x = cos(i) *dist
			y = sin(i) *dist
			locations.append((x+betx,y+bety))

		self.bet_chips.append(Chip(self.drawer,betx,bety,chip_r))
		for i in range(3):
			x,y = locations.pop(0)
			self.bet_chips.append(Chip(self.drawer,x,y,chip_r))

		for i in range(4):
			x,y = locations.pop(0)
			self.earnings_chips.append(Chip(self.drawer,x,y,chip_r))


		

	def reset(self):
		self.drawer.itemconfigure(self.turn_highlight, fill=FELT_GREEN, outline=FELT_GREEN)
		self.drawer.itemconfigure(self.card_area, fill=FELT_GREEN)
		self.drawer.itemconfigure(self.name_tag, text='')
		self.drawer.itemconfigure(self.sum_hint_tag, text='')
		self.ready_tag.hide()
		self.seat_notification.hide()
		for chip in self.bet_chips:
			chip.reset()
		for chip in self.earnings_chips:
			chip.reset()
		self.hand.clear()


	def render_updates(self, content, seat, is_me, seat_of_turn):
		if not content['name']: #player leaving ?
			self.reset()
			return;

		if is_me and seat_of_turn:
			color = PURPLE
			fg = WHITE
		elif seat_of_turn:
			color = BLUE
			fg = BLACK
		elif is_me:
			color = ACENT_GREEN
			fg = BLACK
		else:
			color = FELT_GREEN
			fg = BLACK


		if content['ready']:
			self.ready_tag.update("READY")
		else:
			self.ready_tag.hide()

		if content['active']: self.hand.render_updates(content['cards'])
		if self.drawer.done_dealing(seat):

			self.drawer.itemconfigure(self.turn_highlight, fill=color, outline=color)
			self.drawer.itemconfigure(self.name_tag,fill=fg)
			self.drawer.itemconfigure(self.card_area, fill=color)
			self.drawer.itemconfigure(self.name_tag, text=content['name'])

			if content['active']:
				self.drawer.itemconfigure(self.sum_hint_tag, text='/'.join([str(val) for val in content['sum']]))
				if min(content['sum']) > 21:
					self.seat_notification.update("BUST")
			
			for chip, amount in zip(self.earnings_chips,content['earnings']):
				chip.render_updates(amount)

			for chip, amount in zip(self.bet_chips,content['bet']):
				chip.render_updates(amount)

			
			

class SmartLabel():
	def __init__(self, drawer_manager, x, y, font, fg, bg=None):
		self.drawer = drawer_manager
		self.x, self.y = x,y
		self.font_data = font
		self.fg = fg
		self.bg = bg
		self.active = False
		self.message = ''
		self.padding = 5

		self.text = self.drawer.create_text(x,y,font=font, fill=self.fg, text=self.message, state='hidden')

		self.components = [self.text]
		if self.bg:
			self.bbox = self.drawer.create_rectangle(x,y,x,y,fill=self.bg,outline=self.bg, state='hidden')
			self.components.insert(0,self.bbox)		

	def update(self,message=None):
		self.active = True
		if message:
			self.message = message

		for component in self.components:
			self.drawer.tag_raise(component)
			self.drawer.itemconfigure(component, state='normal')

		self.drawer.itemconfigure(self.text,text=self.message)

		if self.bg:
			x1, y1, x2, y2 = self.drawer.bbox(self.text)
			self.drawer.coords(self.bbox, x1-self.padding, y1-self.padding, x2+self.padding, y2+self.padding)

	def hide(self):
		self.active = False
		for component in self.components:
			self.drawer.itemconfigure(component, state='hidden')

class Hand():
	def __init__(self, drawer_manager, seat, x, y, offset=(35,5)):
		self.x, self.y = x,y
		self.offset = offset
		self.cards = []
		self.drawer = drawer_manager
		self.seat_index = seat

	def clear(self):
		for card in self.cards:
			obj, front, back, pos = card
			self.drawer.master.animations.append(
				DiscardCardAnimation(
					self.drawer,
					obj,
					pos,
					(W,self.drawer.deck_location[1]),
					0.75,
					0,
					card
					)
			)
		self.cards = []

	def render_updates(self, cards, refresh=False):
		if refresh: self.clear()
		cards_on_server = len(cards) 
		cards_in_hand = len(self.cards)

		if cards_on_server == cards_in_hand: return

		for i in range(cards_in_hand, cards_on_server):
			card_name, card_suit = cards[i]

			#self.hand.add_card(find_card_path('A','spades'), (0.5,0)) # (0.5,i*0.5)
			self.add_card(find_card_path(card_name,card_suit),(DEAL_SPEED,0))

		for card in self.cards:
			self.drawer.tag_raise(card)

	def scale_card(self,path):
		if not path: return None
		img = Image.open(path)
		scaled_img = img.resize((CARD_W,CARD_H))
		return ImageTk.PhotoImage(scaled_img)


	def add_card(self, card_path, animation_info=None):
		n = len(self.cards)
		final_x, final_y = self.x + self.offset[0] * n, self.y + self.offset[1] * n

		start_x, start_y = final_x, final_y

		img = self.scale_card(card_path)
		inital_image = img
		if animation_info:
			card_back = self.scale_card(find_card_path('hidden','hidden'))
			start_x, start_y = self.drawer.deck_location
			inital_image = card_back
		else: 
			card_back = None
		

		card_obj = self.drawer.create_image(start_x, start_y, anchor='nw', image=inital_image, state='hidden')

		self.cards.append([card_obj, card_back, img, (final_x,final_y)])

		if animation_info: # only animate if a delay is given
			duration, delay = animation_info

			
			self.drawer.master.animations.append(
				DealCardAnimation(
					self.drawer,
					card_obj,
					img,
					(start_x, start_y),
					(final_x, final_y),
					duration,
					DELAY * sum(self.drawer.cards_to_deal), # cards_to_deal delay
					self.seat_index,
					)
			)
			self.drawer.cards_to_deal[self.seat_index] += 1
		else:
			self.drawer.itemconfigure(card_obj,state='normal')

class DealCardAnimation(Animation):
	def __init__(self, drawer, image, card_face, start_coords, end_coords, duration, delay, seat_index):
		super().__init__(self.move, self.clean_up, duration, delay)
		self.drawer = drawer
		self.image = image
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
		self.drawer.itemconfigure(self.image,state='normal')
		print('update')
		self.coords = (self.coords[0] + self.speed_x * dt, self.coords[1] + self.speed_y * dt)
		self.drawer.coords(self.image, self.coords[0], self.coords[1])
		self.drawer.tag_raise(self.image)
		x, y = self.coords
		margin = 15
		return (self.end_coords[0] - margin <= x <= self.end_coords[0] + margin) and \
			(self.end_coords[1] - margin <= y <= self.end_coords[1] + margin)

	def clean_up(self):
		self.drawer.cards_to_deal[self.seat_index] -= 1
		self.drawer.coords(self.image, self.end_coords[0],self.end_coords[1])

		if self.card_face:
			self.drawer.itemconfigure(self.image, image=self.card_face)

		del self.card_face
		del self

class DiscardCardAnimation(Animation):
	def __init__(self, drawer, image, start_coords, end_coords, duration, delay, card_data):
		super().__init__(self.move, self.clean_up, duration, delay)
		self.drawer = drawer
		self.image = image
		self.start_coords = start_coords
		self.end_coords = end_coords
		self.delay = delay
		self.duration = duration
		self.coords = self.start_coords

		self.speed_x = (self.end_coords[0] - self.start_coords[0])/ self.duration
		self.speed_y = (self.end_coords[1] - self.start_coords[1])/ self.duration 
		self.card_data = card_data

	def move(self, dt):
		print('update')
		self.coords = (self.coords[0] + self.speed_x * dt, self.coords[1] + self.speed_y * dt)
		self.drawer.coords(self.image, self.coords[0], self.coords[1])
		self.drawer.tag_raise(self.image)
		x, y = self.coords
		margin = 15
		return (self.end_coords[0] - margin <= x <= self.end_coords[0] + margin) and \
			(self.end_coords[1] - margin <= y <= self.end_coords[1] + margin)

	def clean_up(self):
		self.drawer.coords(self.image, self.end_coords[0],self.end_coords[1])
		del self.card_data
		del self


class Dealer():
	def __init__(self, drawer_manager, x, y, w, h):
		self.drawer = drawer_manager
		self.hand = Hand(self.drawer, -1, x - (w/2) + (w*0.05),y - (h/2) + (h*0.1), (110,0))
		self.play_area = self.drawer.create_rectangle(x-(w/2),y-(h/2),x+(w/2),y+(h/2),fill=FELT_GREEN,outline=YELLOW,width=3,tags='table')
		self.sum_label = self.drawer.create_text(x-(w/1.7), y,text='', font=('Arial',18),fill=GOLD)

		self.dealer_notification = SmartLabel(self.drawer, x, y, ('Arial',48, 'bold'), 'red', 'black')

		self.fake_deck_cards = 15


		self.is_last_hand = True

		self.deck = Hand(self.drawer, None, x+(w/2)+(CARD_W/3), y-(CARD_H/2), (1,-1))
		self.deck_location = (x+(w/2)+(CARD_W/3), y-(CARD_H/2))

		self.has_revealed_hidden = False


	def render_updates(self,content):
		if not self.has_revealed_hidden and content['turn_index'] == content['max_players']: 
			self.has_revealed_hidden = True

			first_card = content['dealer'][0]
			im = self.hand.scale_card(find_card_path(first_card[0],first_card[1]))
			print(find_card_path(first_card[0],first_card[1]))
			self.drawer.itemconfigure(self.hand.cards[0][0],image=im)
			self.hand.cards[0][2] = im

		self.hand.render_updates(content['dealer'])

		if not (sum(self.drawer.cards_to_deal) == 0 and self.drawer.done_dealing(-1)): return		

		self.drawer.itemconfigure(self.sum_label, text=content['dealer_sum'])
		#notifications
		if content['dealer_sum'] != '?':

			self.drawer.tag_raise(self.dealer_notification)
			dealer_sum = int(content['dealer_sum'])
			message = None
			if dealer_sum == 21 and len(content['dealer']) == 2: #delt blackjack
				message = "Black Jack"
			elif dealer_sum > 21:
				message = "Bust"

			if message:
				self.dealer_notification.update(message)



		deck_percentange = content['deck'][0] / content['deck'][1]
		fake_percentage = len(self.deck.cards)/self.fake_deck_cards

		if deck_percentange < fake_percentage:
			self.deck.cards.pop(-1)
		#								this means there was a shuffle between refreshes
		elif len(self.deck.cards) != self.fake_deck_cards and (deck_percentange == 1 or (self.is_last_hand and not content['deck'][2] )): 
			self.simulate_shuffle(deck_percentange)
		
		self.is_last_hand = content['deck'][2]

	def simulate_shuffle(self, percentage):
		self.deck.clear()
		for i in range(int(percentage * self.fake_deck_cards)):
			self.deck.add_card(find_card_path('hidden','hidden'))


	def reset(self):
		# self.drawer.itemconfigure(self.dealer_notification, text='')
		self.has_revealed_hidden = False
		self.dealer_notification.hide()
		self.hand.clear()

if __name__ == '__main__':
	from faker import Faker

	if len(sys.argv) != 2:
		name = Faker().first_name()
	else:
		name = sys.argv[1]

	app = App(name, 50000)

	app.start()