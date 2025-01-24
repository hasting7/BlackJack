from Cards import Deck

from random import choice

class PlayerData():
	def __init__(self, player_id, seat, money_updater, leave_updater):
		self.id = player_id
		self.money_updater = money_updater
		self.leave_updater = leave_updater

		self.money = self.money_updater(0)
		self.bet = 0
		self.earnings = []
		self.hand = []
		self.doubled_down = False

		self.seat = seat

		self.in_hand = False

		self.ready = False

	def share_hand(self):
		cards = []

		for card in self.hand:
			cards.append(card.information)

		return cards


	def end_of_hand(self):
		self.bet = 0
		self.earnings = []
		self.hand = []
		self.in_hand = False
		self.doubled_down = False

	def payout(self, change):
		self.money = self.money_updater(change)


class BlackJackTable():
	def __init__(self, min_bet, max_players):
		self.players = {}
		self.min_bet = min_bet
		self.max_players = 6
		self.players_at_table = 0

		self.deck = Deck(6)

		self.ready_threshold = 0.4

		# turn is based on active_player array
		self.in_progress = False
		self.turn = None
		self.players_done = None
		self.hand_done = None

		self.dealer_hand = []
		self.dealer_bust = False

		# self.active_players = [None] * self.max_players
		self.players_in_hand = 0

		self.open_seats = list(range(0,self.max_players))
		self.seats = [None] * self.max_players

	def has_room(self):
		return self.players_at_table < self.max_players

	def start_hand(self):
		if self.in_progress: return False

		self.players_in_hand = 0
		for pid, player in self.players.items():
			print(player.id, player.bet, player.money)
			if player.bet > 0:
				player.money = player.money_updater( -1 * player.bet)
				player.in_hand = True
				player.ready = False
				self.players_in_hand += 1 
			else:
				player.in_hand = False

		if self.players_in_hand == 0: return False

		# self.active_players = sorted(players, key = lambda x : self.players[x].seat)
		self.turn = -1
		self.in_progress = True
		self.players_done = False
		self.dealer_bust = False
		self.hand_done = False


		for player_id in self.seats:
			if player_id and self.players[player_id].in_hand:
				for i in range(2):
					card = self.deck.draw()
					self.players[player_id].hand.append(card)

		for i in range(2):
			card = self.deck.draw()
			self.dealer_hand.append(card)

		if self.dealer_hand[1].name == 'A':
			hand_value = self.smart_sum(self.dealer_hand)
			if 21 in hand_value:
				self.turn = self.max_players - 1
				# dealer got blackjack

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
		for player_id in self.seats:
			if player_id and self.players[player_id].in_hand:
				self.players[player_id].end_of_hand()

		self.turn = None
		self.in_progress = False
		self.players_done = None
		self.dealer_hand = []

		if self.deck.last_hand:
			self.deck.reset()

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
			if 21 in possible:
				final_possible.add(21)
			elif min(possible) > 21:
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

		seat = choice(self.open_seats)
		self.open_seats.remove(seat)

		self.seats[seat] = player_id

		self.players[player_id] = PlayerData(player_id, seat, money_function, leave_funtion)
		self.players_at_table += 1


		print("Player %s joined the table, there are %d players at the table"%(player_id, self.players_at_table))
		return True


	def leave_table(self, player_id):
		if self.players[player_id].in_hand: return False

		seat = self.players[player_id].seat

		self.seats[seat] = None

		self.open_seats.append(seat)

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
		# player.bet *= 2 # double bet

		player.earnings.append(player.bet)

		# draw card
		card = self.deck.draw()
		player.hand.append(card)

		player.doubled_down = True


		self.next_turn()

		return True


	def stand(self, player_id):
		if not self.is_allowed(player_id): return False

		self.next_turn()

		return True

	def bet(self, player_id, amount):
		if amount != 0:
			if self.players[player_id].in_hand or self.players[player_id].money < amount or amount < self.min_bet: return False
		else:
			self.players[player_id].ready = False

		self.players[player_id].bet = amount

		
		return True

	def toggle_ready(self,player_id):
		ready = self.players[player_id].ready

		if self.in_progress: return False
		if not ready and self.players[player_id].bet == 0: return False # cannot ready if no bet

		self.players[player_id].ready = not ready

		count_ready = 0
		count_active = 0
		for player_id in self.seats:
			if player_id:
				player_obj = self.players[player_id]
				if player_obj.ready: count_ready += 1
				count_active += 1

		if count_ready/count_active >= self.ready_threshold:
			self.start_hand()


	def is_allowed(self, player_id):
		return self.in_progress and self.players_done == False and self.seats[self.turn] == player_id

	def next_turn(self):
		self.turn = self.turn + 1

		while (self.turn < self.max_players):
			if self.seats[self.turn] != None and self.players[self.seats[self.turn]].in_hand:
				break
			self.turn += 1

		if self.turn >= self.max_players:
			self.players_done = True

			self.dealers_turn()

		else:
			hand = self.players[self.seats[self.turn]].hand
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

		for player_id in self.seats:
			if player_id and self.players[player_id].in_hand:
				player = self.players[player_id]

				hand_value = max(self.smart_sum(player.hand))

				multiplier = 1

				# at this moment player.bet is the inital bet regarless of double down

				# if player doubled down then player.doudbe_down and len(player.earnings) = 1
				# because we add the extra token as the earnings 

				final_pot = player.bet * (2 if player.doubled_down else 1)

				# the final pot will equal whatever the player has taken out of their wallet



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

				# what they bet - what they won
				# earnings is what they gain from the bank
				earnings = int(final_pot * multiplier) - final_pot

				# # if the player oubled down and won
				# if player.doubled_down and earnings > 0:
				# 	# give then two extra chips (should be 3 extra chips total)
				# 	for i in range(2):
				# 		player.earnings.append(earnings)
				# elif earnings == 0: # if the player did not double down or did not win
				# 	player.earnings.append(max(0, earnings))
				# else:
				# 	player.earnings = []

				if player.doubled_down:
					# did double down
					if earnings > 0:
						# won on double donw
						for i in range(2):
							player.earnings.append(earnings)
					if earnings == 0:
						# pushed on double down
						# do nothign
						pass

					else:
						# lost on double down
						player.earnings = []

				else:
					#did not double down
					if earnings > 0:
						player.earnings.append(earnings)
						#won

					else:
						#lost or pushed 
						pass


					

				player.payout(int(final_pot * multiplier))

				if multiplier == 0:
					player.bet = 0
				

		self.hand_done = True


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

