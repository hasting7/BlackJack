from StatusCodes import *
import socket, datetime, sys, json, os, time
from Cards import terminal_name
# from VisualisedBoard import App

class Player():
	def __init__(self, name, money):
		self.server = socket.socket()
		self.server.connect(('0.0.0.0', PORT))

		self.last_refreshed = datetime.datetime.now()

		status, content = self.take_action(JOIN, [name,money])
		

		self.is_turn = False
		self.should_refresh = False

	def take_action(self, action_name, args, buffer_size=1024):
		final_call = action_name + " " + " ".join([str(arg) for arg in args]) if args else action_name
		self.server.send(final_call.encode())

		response = self.server.recv(buffer_size).decode()
		json_resp = json.loads(response)

		server_update_time = datetime.datetime.fromisoformat(json_resp['last_updated_time'])

		if action_name == VIEW:
			self.last_refreshed = datetime.datetime.now()
		if self.last_refreshed < server_update_time:
			self.should_refresh = True

		return json_resp['status'], json_resp['content']


	def mainloop(self):
		last_update = time.time()
		delta = 0
		while (1):
			if last_update + delta < time.time():
				last_update = time.time()
				status, content = self.take_action(VIEW, None)
				if status == SUCCESS:
					display(content)

			command = input("Type Ready: ")

			status, content = self.take_action(command, None)
			print("%s\n%s"%(status, content))

			if status == CLOSED:
				break


		self.server.close()


def center(text, space):
	padding = space - len(text)
	left_padding = padding // 2
	right_padding = padding - left_padding

	return ' '*left_padding+text+' '*right_padding

def player_area_generator(player_data, is_turn, is_me, width, padding=3):
	sum_hint = player_data['sum']

	hint_display = str(sum_hint[0]) if len(sum_hint) == 1 else '/'.join([str(value) for value in sum_hint])

	if is_turn:
		wrapper = "\033[42m%s\033[0m"
	elif is_me:
		wrapper = "\033[100m%s\033[0m"
	else:
		wrapper = "%s"
	bet = '$0' if not player_data['bet'] else '$%s'%str(player_data['bet'])
	yield wrapper%center(bet,width)
	yield wrapper%' '*width
	len_hint_display = len(hint_display) + padding
	hand = ' '.join([terminal_name(name, suit) for name, suit in player_data['cards']])
	yield wrapper%(center(hand, width - len_hint_display)+hint_display+' '*padding)
	yield wrapper%' '*width
	data_length = len(player_data['name']) + len(str(player_data['money'])) + 1 + padding * 2
	yield wrapper%((' '*padding)+player_data['name']+(' '*(width -data_length))+'$'+str(player_data['money'])+(' '*padding))
	yield wrapper%center("seat: %d"%player_data['seat'],width)
	yield wrapper%' '*width
	yield None


def display(board_data):

	if board_data['player_count'] == 0: return

	player_area = 40
	screen_width = player_area * board_data['player_count']
	
	os.system('clear')

	dealer_string = ' '.join([terminal_name(name, suit) for name, suit in board_data['dealer']])

	print(center("Dealer",screen_width))
	print()
	print(center(dealer_string,screen_width))
	print(center(board_data['dealer_sum'],screen_width))
	print()
	
	generators = [
		player_area_generator(
			player,board_data['turn_index'] == i, 
			board_data['index'] == i,
			player_area
		) for i, player in enumerate(board_data['players'])
	]

	terminated = False
	while not terminated:
		complete_line = ''
		for gen in generators:
			line = next(gen)
			if not line: terminated = True
			else: complete_line += line

		print(complete_line)



if __name__ == '__main__':
	from faker import Faker

	fake = Faker()
	p = Player(fake.first_name(), 500)



	p.mainloop()

