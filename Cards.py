import random, os, sys
from PIL import Image


DECK_SIZE = 52

SPADES = ("\u2660",'spades')  # Spades (♠)
CLUBS = ("\u2663",'clubs')  # Clubs (♣)
DIAMONDS = ("\u2666",'diamonds')  # Diamonds (♦)
HEARTS = ("\u2665",'hearts')  # Hearts (♥)

SUITS = [SPADES, HEARTS, CLUBS, DIAMONDS]

SUIT_DATA = [
	('A', [1, 11]),
	('2', [2]),
	('3', [3]),
	('4', [4]),
	('5', [5]),
	('6', [6]),
	('7', [7]),
	('8', [8]),
	('9', [9]),
	('10', [10]),
	('J', [10]),
	('Q', [10]),
	('K', [10])
]

def construct_deck():
	cards = []
	for suit in SUITS:
		for card, values in SUIT_DATA:
			cards.append(Card(card, suit, values))
	return cards

class Card():
	def __init__(self, name, suit, values):
		self.name = name
		self.suit_symbol, self.suit_name = suit
		self.values = values

		self.information = [self.name, self.suit_name]

		self.path = find_card_path(self.name, self.suit_name)

	def __str__(self):
		return "%s%s"%(self.name, self.suit_symbol)

	def __repr__(self):
		return self.__str__()

	def show(self):
		im = Image.open(self.path)
		im.show()

class Deck():
	def __init__(self, deck_count, last_hand_percent=0.08):
		self.deck = []
		self.deck_count = deck_count
		self.last_hand_percent = last_hand_percent
		self.full_deck_size = self.deck_count * DECK_SIZE
		self.cards_remaining = self.full_deck_size

		self.last_hand = False
		self.reset()

	def draw(self):
		if self.full_deck_size * self.last_hand_percent > self.cards_remaining: self.last_hand = True
		self.cards_remaining -= 1
		return self.deck.pop(0)

	def shuffle(self):
		random.shuffle(self.deck) 

	def reset(self):
		self.last_hand = False
		self.cards_remaining = self.full_deck_size
		self.deck = []
		for i in range(self.deck_count):
			self.deck += construct_deck()
		self.shuffle()

	def last_hand(self):
		return len(self.deck) < self.full_deck_size * self.last_hand_percent

def find_card_path(name, suit):
	if getattr(sys, "frozen", False):  # Bundled as an executable
		base_path = sys._MEIPASS
	else:
		base_path = os.path.abspath(".")
	return os.path.join(base_path,'card_images','%s_%s.png'%(name,suit))

def terminal_name(name,suit):
	symbol = "?"
	for suit_type in SUITS:
		if suit == suit_type[1]: 
			symbol = suit_type[0]

	if symbol == "?": name = ''

	return "%s%s"%(name,symbol)

if __name__ == "__main__":
	test = Deck(3)

	print(test.deck)

	card = test.draw()

	card.show()
