from tkinter import *
from PIL import Image,ImageTk

from math import sin, cos, radians
from time import sleep

from Cards import Deck, find_card_path

from Client import Player

from StatusCodes import *

W,H = (1200, 600)
SEATS = 6

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



class App(Tk):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		screen_width = self.winfo_screenwidth()
		screen_height = self.winfo_screenheight()

		user_action_height = 100

		try:
			self.player_client = Player("Bot", 1000)
		except:
			print("No Server Running / Cannot Connect")
			exit(1)

		self.action_queue = []

		self.title("BlackJack")
		self.resizable(0,0)
		self.geometry("%sx%s+%s+%s"%(W,H+user_action_height,(screen_width // 2) - (W // 2),(screen_height // 2) - ((H+user_action_height) // 2)))

		self.table_can = Table(self, width=W, height=H, bd=0, highlightthickness=0, bg=FELT_GREEN)
		self.table_can.pack()

		self.user_actions = UserActions(self, width=W, height=user_action_height, bg=BROWN)
		self.user_actions.pack()
		self.user_actions.pack_propagate(0)

		self.bind('q', self.close)

		self.bind('s', self.table_can.render_updates)

		self.ready_to_quit = False

	def render_updates(self, content):
		if content['player_count'] == 0:
			 # this is between rounds
			 # make it so it doesnt reset over and over and over
			 self.table_can.reset()
		else:
			self.table_can.render_updates(content)

			personal_money = content['players'][content['index']]['money']
			print(personal_money)

			self.user_actions.render_updates(personal_money)

	def close(self, e):
		status, content = self.player_client.take_action(LEAVE,None)
		if status == SUCCESS:
			self.ready_to_quit = True

	def start(self):
		while not self.ready_to_quit:
			self.update_idletasks()
			self.update()

			if len(self.action_queue) != 0:
				action = self.action_queue.pop(0)

				status, content = self.player_client.take_action(action,None)
				# take action

			# refresh / process updates
			status, content = self.player_client.take_action(VIEW,None)
			if status == SUCCESS:
				self.render_updates(content)


			sleep(0.01)

		print("CLOSING")

	def do_action(self, action):
		self.action_queue.append(action)

class UserActions(Frame):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.bet_amount = 0

		third = self['width']*0.33

		self.money_frame = Frame(self,height=self['height'],width=third,bg=self['bg'])
		self.money_frame.pack(side="left")

		self.bet_frame = Frame(self, height=self['height'],width=third,bg=self['bg'])
		self.bet_frame.pack(side="left")

		self.bet_changer = Frame(self.bet_frame, height=self['height'],width=third,bg=self.bet_frame['bg'])
		self.bet_changer.pack(side="top")
		# self.bet_changer.pack_propagate(0)

		self.action_frame = Frame(self,height=self['height'],width=third,bg=self['bg'])
		self.action_frame.pack(side="left")
		self.action_frame.pack_propagate(0)

		font_size = 18
		bet_inc_size = 24

		self.hit_btn = Button(self.action_frame, text='Hit', command=self.hit,highlightbackground=self.action_frame['bg'], bg=self.action_frame['bg'], font=('Arial',font_size))
		self.hit_btn.pack(side="left", fill="both", expand=True)

		self.stand_btn = Button(self.action_frame, text='Stand', command=self.stand,highlightbackground=self.action_frame['bg'], bg=self.action_frame['bg'], font=('Arial',font_size))
		self.stand_btn.pack(side="left", fill="both", expand=True)

		self.double_btn = Button(self.action_frame, text='Double', command=self.double,highlightbackground=self.action_frame['bg'], bg=self.action_frame['bg'], font=('Arial',font_size))
		self.double_btn.pack(side="left", fill="both", expand=True)

		self.bet_button = Button(self.bet_frame, text='Place Bet', command=self.bet,highlightbackground=self.bet_changer['bg'], bg=self.bet_changer['bg'], font=('Arial',bet_inc_size-5))
		
		self.increment_bet = Button(self.bet_changer, text='+', command=lambda : self.change_bet(10),highlightbackground=self.bet_changer['bg'], bg=self.bet_changer['bg'], font=('Arial',bet_inc_size))
		self.decrement_bet = Button(self.bet_changer, text='-', command=lambda : self.change_bet(-10),highlightbackground=self.bet_changer['bg'], bg=self.bet_changer['bg'], font=('Arial',bet_inc_size))
		self.bet_view = Label(self.bet_changer, width=8,text='$0', font=("Arial",bet_inc_size),bg=self.bet_changer['bg'])

		self.decrement_bet.pack(side=LEFT,fill='both', anchor=CENTER)
		self.bet_view.pack(side=LEFT,fill='both', anchor=CENTER)
		self.increment_bet.pack(side=LEFT,fill='both', anchor=CENTER)
		self.bet_button.pack(side=BOTTOM,fill='both')

		self.bank_label = Label(self.money_frame,text='',font=('Arial',32),width=10,bg=self.money_frame['bg'])
		self.bank_label.pack()

		self.update_bet_label()

	def change_bet(self, amount):
		self.bet_amount += amount
		self.update_bet_label()

	def update_bet_label(self):
		self.bet_view.config(text='$%d'%self.bet_amount)

	def hit(self):
		print("hitting")
		self.master.do_action(HIT)

	def stand(self):
		print("stading")
		self.master.do_action(STAND)

	def double(self):
		print("double")
		self.master.do_action(DOUBLE)

	def bet(self):
		print("Betting 100")
		self.master.do_action('bet %d'%self.bet_amount)

	def render_updates(self,personal_money):
		self.bank_label.config(text='$%d'%personal_money)



class Table(Canvas):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.seats = []
		self.players = []
		self.dealer = Dealer(self, W/2, 110, 600,180)

		player_space = W / (SEATS + 1)
		y = 425
		x = player_space
		scale = 1.3
		width = CARD_W*scale
		height = CARD_H*scale

		for i in range(SEATS):
			seat = Seat(self, x ,y, width, height)
			self.seats.append(seat)
			x += player_space

	def render_updates(self, content):
		self.dealer.render_updates(content)

		for i, player in enumerate(content['players']):
			seat = self.seats[player['seat']]
			seat.render_updates(player, i == content['index'], i == content['turn_index'])


	def reset(self):
		self.dealer.reset()
		for seat in self.seats:
			seat.reset()



class Seat():
	def __init__(self, drawer_manager, x, y, w, h):
		self.drawer = drawer_manager
		self.hand = Hand(self.drawer,x - (CARD_W /2),y  - (CARD_H /2), (0, 40))

		bet_radius = w*0.2

		radius = x-(w/2)

		betx,bety = (x - (w/2) + bet_radius,y-(1.7*h/2))
		

		self.turn_highlight = self.drawer.create_rectangle(x-(w/1.65),y-(h/1.65),x+(w/1.65),y+(h/1.65), fill=FELT_GREEN, outline=FELT_GREEN, width=1)
		self.card_area = self.drawer.create_rectangle(x-(w/2),y-(h/2),x+(w/2),y+(h/2), fill=FELT_GREEN, outline=YELLOW, width=3)
		self.bet_area = self.drawer.create_oval(betx-bet_radius, bety-bet_radius,betx+bet_radius, bety+bet_radius, fill=FELT_GREEN, outline=YELLOW, width=3)
		self.name_tag = self.drawer.create_text(x,y-(h/2)-10, text='', fill=BLACK)
		self.bet_tag = self.drawer.create_text(betx,bety, text='', fill=BLACK)
		self.sum_hint_tag = self.drawer.create_text(x+bet_radius, bety, text='', fill=GOLD, font=('Arial',18))

	def reset(self):
		self.drawer.itemconfigure(self.turn_highlight, fill=FELT_GREEN, outline=FELT_GREEN)
		self.drawer.itemconfigure(self.card_area, fill=FELT_GREEN)
		self.drawer.itemconfigure(self.name_tag, text='')
		self.drawer.itemconfigure(self.bet_tag, text='')
		self.drawer.itemconfigure(self.sum_hint_tag, text='')

		self.hand.clear()



	def render_updates(self, content, is_me, seat_of_turn):
		color = BLUE if seat_of_turn else FELT_GREEN
		if is_me: color = ACENT_GREEN
		self.drawer.itemconfigure(self.turn_highlight, fill=color, outline=color)
		self.drawer.itemconfigure(self.card_area, fill=color)


		self.drawer.itemconfigure(self.name_tag, text=content['name'])
		self.drawer.itemconfigure(self.bet_tag, text="$%d"%content['bet'])
		self.drawer.itemconfigure(self.sum_hint_tag, text='/'.join([str(val) for val in content['sum']]))

		self.hand.render_updates(content['cards'])


class Hand():
	def __init__(self, drawer_manager, x, y, offset=(35,5)):
		self.x, self.y = x,y
		self.offset = offset
		self.cards = []
		self.drawer = drawer_manager

	def clear(self):
		self.cards = []

	def render_updates(self, cards):
		cards_on_server = len(cards) 
		cards_in_hand = len(self.cards)

		if cards_on_server == cards_in_hand: return

		for i in range(cards_in_hand, cards_on_server):
			card_name, card_suit = cards[i]

			self.add_card(find_card_path(card_name,card_suit))


	def add_card(self, card_path, rotation=0):
		img = Image.open(card_path)

		scaled_img = img.resize((CARD_W,CARD_H))

		rotated_img = scaled_img.rotate(rotation, expand=True)

		tk_img = ImageTk.PhotoImage(rotated_img)

		n = len(self.cards)
		offset_x, offset_y = self.offset[0] * n, self.offset[1] * n

		angle_rad = radians(rotation)

		rotated_x = offset_x * cos(angle_rad) - offset_y * sin(angle_rad)
		rotated_y = offset_x * sin(angle_rad) + offset_y * cos(angle_rad)

		final_x = self.x + rotated_x
		final_y = self.y + rotated_y

		self.cards.append((card_path, tk_img))

		self.drawer.create_image(final_x, final_y, anchor='nw', image=tk_img)

class Dealer():
	def __init__(self, drawer_manager, x, y, w, h):
		self.drawer = drawer_manager
		self.hand = Hand(self.drawer, x - (w/2) + (w*0.05),y - (h/2) + (h*0.1), (110,0))
		self.play_area = self.drawer.create_rectangle(x-(w/2),y-(h/2),x+(w/2),y+(h/2),fill=FELT_GREEN,outline=YELLOW,width=3)
		self.sum_label = self.drawer.create_text(x-(w/1.7), y,text='', font=('Arial',18),fill=BLACK)

	def render_updates(self,content):
		if content['turn_index'] == content['player_count']: self.hand.clear()
		self.hand.render_updates(content['dealer'])

		self.drawer.itemconfigure(self.sum_label, text=content['dealer_sum'])

	def reset(self):
		self.hand.clear()

if __name__ == '__main__':

	deck = Deck(1).draw()

	app = App()

	app.start()