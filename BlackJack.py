from Cards import Deck

from random import choice

class PlayerData():
	def __init__(self, player_id, seat, money_updater, leave_updater):
		self.id = player_id
		self.money_updater = money_updater
		self.leave_updater = leave_updater

		self.money = self.money_updater(0)
		self.bet = 0
		self.hand = []

		self.seat = seat

		self.in_hand = False

	def share_hand(self):
		cards = []

		for card in self.hand:
			cards.append(card.information)

		return cards


	def end_of_hand(self):
		self.bet = 0
		self.hand = []
		self.in_hand = False

	def payout(self, change):
		self.money = self.money_updater(change)


class BlackJackTable():
	def __init__(self, min_bet, max_players):
		self.players = {}
		self.min_bet = min_bet
		self.max_players = 6
		self.players_at_table = 0

		self.deck = Deck(6)

		# turn is based on active_player array
		self.in_progress = False
		self.turn = None
		self.players_done = None
		self.hand_done = None

		self.dealer_hand = []
		self.dealer_bust = False

		self.active_players = []

		self.seats = list(range(0,self.max_players))

	def has_room(self):
		return self.players_at_table < self.max_players

	def start_hand(self):
		print(self.in_progress)
		if self.in_progress: return False
		print('the issue is no players')

		players = []
		for pid, player in self.players.items():
			print(player.id, player.bet, player.money)
			if player.bet > 0:
				player.in_hand = True
				players.append(pid)
		if len(players) == 0: return False

		self.active_players = sorted(players, key = lambda x : self.players[x].seat)
		self.turn = -1
		self.in_progress = True
		self.players_done = False
		self.dealer_bust = False
		self.hand_done = False

		for player_id in self.active_players:
			for i in range(2):
				card = self.deck.draw()
				self.players[player_id].hand.append(card)

		for i in range(2):
			card = self.deck.draw()
			self.dealer_hand.append(card)

		self.next_turn()

		return True

	def share_dealer_hand(self, hide=0):
		cards = []
		for i in range(len(self.dealer_hand)):
			if i >= hide:
				cards.append(self.dealer_hand[i].information)
			else:
				cards.append(["hidden","hidden"])

		return cards

	def end_hand(self):
		if not self.hand_done: return False
		for player_id in self.active_players:
			self.players[player_id].end_of_hand()

		self.active_players = []
		self.turn = None
		self.in_progress = False
		self.players_done = None
		self.dealer_hand = []

		return True

	def smart_sum(self, hand):
		possible = set([0])
		for card in hand:
			update_possible = set()
			for partial_sum in possible:
				for value in card.values:
					update_possible.add(partial_sum+value)
			possible = update_possible

		final_possible = set()
		if len(possible) == 1:
			final_possible = possible
		else:
			if min(possible) > 21:
				final_possible.add(min(possible))
			
			else:
				for value in possible:
					if value <= 21:
						final_possible.add(value)


		return sorted(list(final_possible))

	def check_bust(self,hand):
		total = 0
		for card in hand:
			value = min(card.values)
			total += value
		return total > 21


	def join_table(self, player_id, money_function, leave_funtion):
		if not self.has_room(): return False

		seat = choice(self.seats)
		self.seats.remove(seat)

		self.players[player_id] = PlayerData(player_id, seat, money_function, leave_funtion)
		self.players_at_table += 1


		print("Player %s joined the table, there are %d players at the table"%(player_id, self.players_at_table))
		return True


	def leave_table(self, player_id):
		if self.players[player_id].in_hand: return False

		self.seats.append(self.players[player_id].seat)

		self.players_at_table -= 1
		self.players[player_id].leave_updater()
		del self.players[player_id]

		print("Player %s left the table, there are %d players at the table"%(player_id, self.players_at_table))

		return True

	def hit(self, player_id, dealing=False):
		#FIX THIS, IF ANYONE GETS A BLACKJACK IT CALLS NEXT_TURN AND SKIP THE FIRST PLAYER REGARDLESS
		if not self.is_allowed(player_id): return False

		card = self.deck.draw()
		self.players[player_id].hand.append(card)

		is_bust = self.check_bust(self.players[player_id].hand)
		if is_bust: self.next_turn()

		hand_value = self.smart_sum(self.players[player_id].hand)
		if 21 in hand_value:
			self.next_turn()

		return True

	def double_down(self, player_id):
		if not self.is_allowed(player_id): return False

		player = self.players[player_id]
		bet = self.players[player_id].bet
		if len(player.hand) != 2: return False # already hit
		if player.money < bet: return False # not enought money

		player.payout(-1 * bet) # remove funds
		player.bet *= 2 # double bet

		# draw card
		card = self.deck.draw()
		player.hand.append(card)


		self.next_turn()

		return True


	def stand(self, player_id):
		if not self.is_allowed(player_id): return False

		self.next_turn()

		return True

	def bet(self, player_id, amount):
		if self.in_progress or self.players[player_id].money < amount or amount < self.min_bet: return False

		self.players[player_id].bet = amount
		self.players[player_id].money = self.players[player_id].money_updater( -1 * amount)
		
		return True

	def is_allowed(self, player_id):
		return self.in_progress and self.players_done == False and self.active_players[self.turn] == player_id

	def next_turn(self):
		self.turn = self.turn + 1

		if self.turn >= len(self.active_players):
			self.players_done = True

			self.dealers_turn()

		else:
			hand = self.players[self.active_players[self.turn]].hand
			hand_value = self.smart_sum(hand)
			if 21 in hand_value:
				self.next_turn()

	def dealers_turn(self):
		while max(self.smart_sum(self.dealer_hand)) <= 16:
			card = self.deck.draw()
			self.dealer_hand.append(card)

		dealer_hand_value = max(self.smart_sum(self.dealer_hand))
		self.dealer_bust = self.check_bust(self.dealer_hand)

		# determine payouts

		for player_id in self.active_players:
			player = self.players[player_id]

			hand_value = max(self.smart_sum(player.hand))

			multiplier = 1



			if hand_value == 21 and len(player.hand) == 2: # delt blackjack
				multiplier = 2.5

			elif hand_value > 21: # player bust 
				multiplier = 0

			elif hand_value == dealer_hand_value: # matches
				multiplier = 1

			elif self.dealer_bust or hand_value > dealer_hand_value: # player wins or dealer busts
				multiplier = 2

			elif hand_value < dealer_hand_value: # player loses
				multiplier = 0

			player.payout(int(player.bet * multiplier))
			player.bet = int(player.bet * multiplier)

		self.hand_done = True


	def payout(self, payouts): #payout is a float which is a bet x payout mutliplier

		for i in range(len(self.active_players)):
			player = self.players[self.active_players[i]]

			player.money_updater(int(player.bet * payout[i]))



if __name__ == '__main__':
	def money_updater(money):
		print("player %s made $%d"%(id,money))
		return 100

	def leave_updater():
		print("player %s is leaving"%(id))

	table = BlackJackTable(15, 6)

	table.join_table('ben', money_updater, leave_updater)
	table.join_table('ryan', money_updater, leave_updater)

	print(table.bet('ben', 50))

