import random

COLORS = 'ABCDEF'

def input_is_sane(user_input):
	if len(user_input) == 4 and not set(user_input) - set(COLORS):
		return True
	return False

def get_random_code():
	code = ''
	for i in range(4):
		code += random.choice(COLORS)
	return code

def get_answer(guess, code):
	black = 0
	white = 0
	remained_guess = []
	remained_code = []
	for i in range(len(guess)):
		if guess[i] == code[i]:
			black += 1
		else:
			remained_guess.append(guess[i])
			remained_code.append(code[i])
	for color in remained_guess:
		if color in remained_code:
			white += 1
			remained_code.remove(color)
	return black, white

def print_history(history):
	for i in range(len(history)):
		print(' #{}    {}  -  correct={} misplaced={}'.format(i + 1, ' | '.join(history[i][0]), history[i][1][0], history[i][1][1]))

def main():
	history = []
	code = get_random_code()
	found = False
	print('Make a guess by choosing 4 symbols from "{}"'.format(COLORS))
	while not found:
		guess = input('Make a guess: ')
		if not input_is_sane(guess):
			print('Invalid input - Choose 4 symbols from "{}"'.format(COLORS))
			continue
		answer = get_answer(guess, code)
		history.append((guess, answer))
		print_history(history)
		if answer == (4, 0):
			found = True
			print('CORRECT!')

if __name__ == '__main__':
	main()