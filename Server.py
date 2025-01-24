from StatusCodes import *
from BlackJack import BlackJackTable
import socket, threading, datetime, json, sys

class AtomicData():
	def __init__(self, init_value=None):
		self.value = init_value

		self.mutex = threading.Lock()

	def set(self, value):
		with self.mutex:
			self.value = value

	def get(self):
		with self.mutex:
			return self.value

	def bump(self, change):
		with self.mutex:
			self.value += change
			return self.value

class ClientInstance:
	def __init__(self, socket, address, thread):
		self.name = AtomicData()
		self.money = AtomicData(0)
		self.address = address
		self.socket = socket
		self.thread = thread

		self.claimed = False

		self.ready = AtomicData(False)
		self.is_playing = AtomicData(False)

class BlackJackServer:
	def __init__(self, port):
		self.socket = socket.socket()
		self.socket.bind(('0.0.0.0', port))
		self.socket.listen(MAX_THREADS)

		self.threads = {}
		self.lock = threading.Lock()

		self.last_updated_time = AtomicData(datetime.datetime.now())

		self.ready_up = AtomicData(0)
		self.in_progress = AtomicData(False)

		self.table = BlackJackTable(15, 6)
		self.table_lock = threading.Lock()


	def update_time(self):
		self.last_updated_time.set(datetime.datetime.now())

	def start(self):
		try:
			while True:
				c, addr = self.socket.accept()
				print(f"Connection accepted from {addr}")
				
				new_thread = threading.Thread(target=self.thread_mainloop, args=(c, addr))
				client_instances = ClientInstance(c, addr, new_thread)
				
				with self.lock:  # Ensure thread list is thread-safe
					self.threads[addr] = client_instances
				
				new_thread.start()
		except KeyboardInterrupt:
			self.shutdown()

	def construct_response(self,content, status):
		time = self.last_updated_time.get().isoformat()

		data = {
			'status' : status,
			'content': content
		}
		# print(json.dumps(data))
		return json.dumps(data)

	def parse_request(self, request, address):

		args = request.split(' ')
		command = args[0]
		args = args[1:]

		status = None
		content = None

		if command == JOIN:
			with self.lock:
				client_data = self.threads[address]

				if not client_data.claimed and self.table.has_room():

					client_data.name.set(args[0])
					client_data.money.set(int(args[1]))
					client_data.claimed = True
					status = SUCCESS
					content = '%s added as a player'%args[0]

					# add to table
					with self.table_lock:
						self.table.join_table(address, client_data.money.bump, lambda : print("No leave function yet"))
				else:
					status = ILLEGAL
					content = 'aleady claimed'

		elif command == LEAVE:
			with self.lock:
				if self.table.leave_table(address):
					status = CLOSED
					content = 'closing connection'
				else:
					content = 'cannot leave during game'
					status = INVALID

		elif command == START:
			with self.table_lock:
				if self.table.start_hand():
					status = SUCCESS
					content = "game started"
				else:
					status = INVALID
					content = "could not start game"

		elif command == END:
			with self.table_lock:
				if self.table.end_hand():
					status = SUCCESS
					content = "hand ended"
				else:
					status = INVALID
					content = "cannot end hand right now it is not over"


		elif command == BET:
			with self.lock:
				client_data = self.threads[address]

				with self.table_lock:
					if self.table.bet(address, int(args[0])):
						print("%s made a bet of $%d"%(client_data.name.get(),int(args[0])))

						status = SUCCESS
						content = 'bet made'

					else:
						status = INVALID
						content = 'error placing bet'

		elif command == HIT:
			with self.table_lock:
				if self.table.hit(address):
					status = SUCCESS
					content = 'hit'

				else:
					status = INVALID
					content = 'error hitting'

		elif command == READY:
			with self.table_lock:
				if self.table.toggle_ready(address):
					status = SUCCESS
					content = 'player ready'

				else:
					status = INVALID
					content = 'cannot ready up right now'

		elif command == DOUBLE:
			with self.table_lock:
				if self.table.double_down(address):
					status = SUCCESS
					content = 'double down'

				else:
					status = INVALID
					content = 'cannot double down'


		elif command == STAND:
			with self.table_lock:
				if self.table.stand(address):
					status = SUCCESS
					content = 'stand'

				else:
					status = INVALID
					content = 'error standing'



		elif command == VIEW:
			status = SUCCESS

			with self.table_lock:
				player_data = []
				for i, player_id in enumerate(self.table.seats):
					if player_id:
						player_obj = self.table.players[player_id]
						if player_obj.in_hand:
							#player is playing
							hand_sum = self.table.smart_sum(player_obj.hand)
							player_data.append({
								'name'  : self.threads[player_id].name.get(),
								'money' : player_obj.money,
								'cards' : player_obj.share_hand(),
								'bet'	: player_obj.bet,
								'sum'	: hand_sum,
								'seat'	: i,
								'active':True,
								'ready' : player_obj.ready,
								'earnings' : player_obj.earnings
							})
						else:
							#player is sitting out
							player_data.append({
								'name'  : self.threads[player_id].name.get(),
								'money' : player_obj.money - sum(player_obj.bet), # THIS IS LOWKEY SKETCHT
								'cards' : None,
								'bet'	: player_obj.bet,
								'sum'	: None,
								'seat'	: i,
								'active': False,
								'ready' : player_obj.ready,
								'earnings' : []
							})
					else:
						player_data.append({
							'name'  : None,
							'money' : None,
							'cards' : None,
							'bet'	: [],
							'sum'	: None,
							'seat'	: i,
							'active':False,
							'ready' : False,
							'earnings' : []
						})

				player_index = -1
				for i in range(len(self.table.seats)):
					if address == self.table.seats[i]:
						player_index = i
						break

				dealer_hand = self.table.share_dealer_hand(0 if self.table.players_done else 1)
				dealer_sum = "?"
				if self.table.players_done:
					dealer_sum = str(max(self.table.smart_sum(self.table.dealer_hand)))

				content = {
					'player_count' : self.table.players_in_hand,
					'index'	: player_index,
					'turn_index' : self.table.turn,
					'dealer' : dealer_hand,
					'dealer_sum' : dealer_sum,
					'players' : player_data,
					'max_players' : self.table.max_players,
					'deck' : [
						self.table.deck.cards_remaining,
						self.table.deck.full_deck_size,
						self.table.deck.last_hand
					],
				}

		return content, status

	def thread_mainloop(self, client, addr):
		try:
			# Placeholder for actual client handling logic
			while True:
				data = client.recv(BUFFER_SIZE).decode()
				if not data:
					break

				content, status = self.parse_request(data, addr)

				response_message = self.construct_response(content, status)

				# print(f"Received from {addr}: {data.decode()}")
				client.send(response_message.encode())  # Echo back the data

				if status == CLOSED:
					with self.lock:
						client_data = self.threads[addr]
						client_data.socket.close()

						del self.threads[addr]
						# client_data.thread.join()
					break
					# close connection 


		except Exception as e:
			raise e
			print(f"Error with client {addr}: {e}")
			with self.table_lock:
				self.table.leave_table(addr)
		finally:
			client.close()
			print(f"Connection with {addr} closed")

	def shutdown(self):
		print("Shutting down...")
		with self.lock:
			for address, client_data in self.threads.items():
				client_data.socket.close()
				client_data.thread.join()
		self.socket.close()
		print("Server closed")

# game thread
# create a request queue and a action queue


if __name__ == '__main__':
	port = PORT
	if len(sys.argv) == 2:
		try:
			port = int(sys.argv[1])
		except:
			print("invalid port")

	print("server starting on port: %d"%port)

	server = BlackJackServer(port)
	server.start()
