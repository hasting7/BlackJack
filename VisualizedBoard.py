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
PURPLE='#4B0082'
WHITE='#FFFFFF'

CHIP_COLORS = ["#F44336", "#FF9800", "#FFEB3B", "#4CAF50", "#2196F3", "#9C27B0", "#00BCD4", "#FF5722", "#3F51B5", "#CDDC39"]
CHIP_FG = [WHITE, BLACK, BLACK, WHITE, WHITE, WHITE, BLACK, BLACK, WHITE, BLACK]
CHIP_DENOMINATIONS = [5, 25, 50, 100, 250, 500]



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

		self.bet_mods = []

		self.bet_amount = 0

		third = self['width']*0.33

		# self.money_frame = Frame(self,height=self['height'],width=third,bg=self['bg'])
		# self.money_frame.pack(side="left")

		self.bet_frame = Frame(self, height=self['height'],width=third,bg=self['bg'])
		self.bet_frame.pack(side="left")


		self.action_frame = Frame(self,height=self['height'],width=third,bg=self['bg'])
		self.action_frame.pack(side="left")
		# self.action_frame.pack_propagate(0)

		font_size = 18
		bet_inc_size = 24


		self.hit_btn = Button(self.action_frame, text='Hit', command=self.hit,highlightbackground=self.action_frame['bg'], bg=self.action_frame['bg'], font=('Arial',font_size))
		self.hit_btn.pack(side="left", fill="both", expand=True)

		self.stand_btn = Button(self.action_frame, text='Stand', command=self.stand,highlightbackground=self.action_frame['bg'], bg=self.action_frame['bg'], font=('Arial',font_size))
		self.stand_btn.pack(side="left", fill="both", expand=True)

		self.double_btn = Button(self.action_frame, text='Double', command=self.double,highlightbackground=self.action_frame['bg'], bg=self.action_frame['bg'], font=('Arial',font_size))
		self.double_btn.pack(side="left", fill="both", expand=True)

		for chip_value, chip_color in zip(CHIP_DENOMINATIONS, CHIP_COLORS):
			editor = BetModifier(chip_value,self.update_bet_label, self.bet_frame,width=50,height=self.bet_frame['height'],bg=chip_color)
			editor.pack(side=LEFT)
			editor.pack_propagate(0)
			self.bet_mods.append(editor)


		# self.bank_label = Label(self.money_frame,text='',font=('Arial',32),width=10,bg=self.money_frame['bg'])
		# self.bank_label.pack()

		self.bet_view = Label(self.bet_frame,text='$0',font=('Arial',32),width=10,bg=self.bet_frame['bg'])
		self.bet_view.pack(side=LEFT)

		self.make_bet = Button(self.bet_frame, text='Place Bet', command=self.bet,highlightbackground=self.bet_frame['bg'], bg=self.bet_frame['bg'], font=('Arial',font_size))
		self.make_bet.pack(side="left", fill="y", expand=True)


		self.update_bet_label()

		#remove this later
		self.start_btn = Button(self.action_frame, text='Start', command=self.start,highlightbackground=self.action_frame['bg'], bg=self.action_frame['bg'], font=('Arial',font_size))
		self.start_btn.pack(side="left", fill="both", expand=True)

		self.end_btn = Button(self.action_frame, text='End', command=self.end,highlightbackground=self.action_frame['bg'], bg=self.action_frame['bg'], font=('Arial',font_size))
		self.end_btn.pack(side="left", fill="both", expand=True)
		#remove this lateer

	def change_bet(self, amount):
		self.bet_amount += amount
		self.update_bet_label()

	def update_bet_label(self):
		total_bet = 0
		for editor in self.bet_mods:
			total_bet += editor.get_total()

		self.bet_amount = total_bet

		self.bet_view.config(text='$%d'%self.bet_amount)

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

	def double(self):
		print("double")
		self.master.do_action(DOUBLE)

	def bet(self):
		self.master.do_action('bet %d'%self.bet_amount)

	def render_updates(self,personal_money):
		return
		# self.bank_label.config(text='$%d'%personal_money)

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
		self.hand = Hand(self.drawer,x - (CARD_W /2),y  - (CARD_H /2), (0, 25))

		bet_radius = w*0.25

		betx,bety = (x - (w/2) + bet_radius,y-(1.7*h/2))

		chip_r = 0.75*bet_radius
		

		self.turn_highlight = self.drawer.create_rectangle(x-(w/1.65),y-(h/1.65),x+(w/1.65),y+(h/1.65), fill=FELT_GREEN, outline=FELT_GREEN, width=1)
		self.card_area = self.drawer.create_rectangle(x-(w/2),y-(h/2),x+(w/2),y+(h/2), fill=FELT_GREEN, outline=YELLOW, width=3)
		self.bet_area = self.drawer.create_oval(betx-bet_radius, bety-bet_radius,betx+bet_radius, bety+bet_radius, fill=FELT_GREEN, outline=YELLOW, width=3)
		self.name_tag = self.drawer.create_text(x,y-(h/2)-10, text='', fill=BLACK)
		self.bet_tag = self.drawer.create_text(betx,bety, text='', fill=BLACK,font=('Arial',16))
		self.sum_hint_tag = self.drawer.create_text(x+bet_radius, bety, text='', fill=GOLD, font=('Arial',18))
		self.bust_label = self.drawer.create_text(x,y,text='',fill='red',font=('Arial',48, 'bold'))
		self.chip = self.drawer.create_oval(betx-chip_r,bety-chip_r,betx+chip_r,bety+chip_r,fill=WHITE,outline=BLACK,width=2,state='hidden')

	def reset(self):
		self.drawer.itemconfigure(self.turn_highlight, fill=FELT_GREEN, outline=FELT_GREEN)
		self.drawer.itemconfigure(self.card_area, fill=FELT_GREEN)
		self.drawer.itemconfigure(self.name_tag, text='')
		self.drawer.itemconfigure(self.bet_tag, text='')
		self.drawer.itemconfigure(self.sum_hint_tag, text='')
		self.drawer.itemconfigure(self.bust_label,text='')
		self.drawer.itemconfigure(self.chip,state='hidden')
		self.drawer.itemconfigure(self.bet_tag,fill=BLACK)

		self.hand.clear()


	def render_updates(self, content, is_me, seat_of_turn):
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

		self.drawer.itemconfigure(self.turn_highlight, fill=color, outline=color)
		self.drawer.itemconfigure(self.name_tag,fill=fg)
		self.drawer.itemconfigure(self.card_area, fill=color)

		bust_text = 'BUST' if min(content['sum']) > 21 else ''


		self.drawer.itemconfigure(self.bust_label, text=bust_text)
		self.drawer.tag_raise(self.bust_label)
		self.drawer.itemconfigure(self.name_tag, text=content['name'])
		self.drawer.itemconfigure(self.sum_hint_tag, text='/'.join([str(val) for val in content['sum']]))
		self.hand.render_updates(content['cards'])


		# make bets look good

		# make this only run when just starting

		chip_index = -1
		for i in range(len(CHIP_DENOMINATIONS)-1, 0, -1):
			if content['bet'] - CHIP_DENOMINATIONS[i] >= 0:
				chip_index = i
				break

		if chip_index != -1:
			chip_bg = CHIP_COLORS[chip_index]
			chip_fg = CHIP_FG[chip_index]
			state = 'normal'

		else:
			chip_bg = WHITE
			chip_fg = BLACK
			state = 'hidden'

		self.drawer.itemconfigure(self.chip, state=state, fill=chip_bg)

		self.drawer.itemconfigure(self.bet_tag, text="$%d"%content['bet'],fill=chip_fg)
		self.drawer.tag_raise(self.bet_tag)
		


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
		self.sum_label = self.drawer.create_text(x-(w/1.7), y,text='', font=('Arial',18),fill=GOLD)

		self.fake_deck_cards = 15


		self.is_last_hand = True

		self.deck = Hand(self.drawer, x+(w/2)+100, y-(h/2)+10, (1,-1))
		

	def render_updates(self,content):
		if content['turn_index'] == content['player_count']: self.hand.clear()
		self.hand.render_updates(content['dealer'])

		self.drawer.itemconfigure(self.sum_label, text=content['dealer_sum'])

		deck_percentange = content['deck'][0] / content['deck'][1]
		fake_percentage = len(self.deck.cards)/self.fake_deck_cards

		if deck_percentange < fake_percentage:
			self.deck.cards.pop(-1)
		#								this means there was a shuffle between refreshes
		elif deck_percentange == 1 or (self.is_last_hand and not content['deck'][2] ): 
			self.simulate_shuffle(deck_percentange)
		
		self.is_last_hand = content['deck'][2]

	def simulate_shuffle(self, percentage):
		self.deck.clear()
		for i in range(int(percentage * self.fake_deck_cards)):
			self.deck.add_card(find_card_path('hidden','hidden'))


	def reset(self):
		self.hand.clear()

if __name__ == '__main__':

	deck = Deck(1).draw()

	app = App()

	app.start()