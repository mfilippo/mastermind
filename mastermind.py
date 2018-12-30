# -*- coding: utf-8 -*-

"""
Scripts implementing the famous mastermind game. The user has to guess a code made by four symbols.
The script can be executed with:

    $ python3 mastermind.py
"""

import random
import itertools
from abc import ABC, abstractmethod

COLORS = 'ABCDEF'


class CodeMaker(ABC):
    """
    Abstract class defining the Code Maker behaviour.
    """

    @abstractmethod
    def make_code(self):
        pass

    @abstractmethod
    def answer(self, guess):
        pass


class CodeBreaker(ABC):
    """
    Abstract class defining the Code Breaker behaviour.
    """

    @abstractmethod
    def initial_guess(self):
        pass

    @abstractmethod
    def guess(self, answer):
        pass


class ComputerCodeMaker(CodeMaker):
    """
    Implementation of Code Maker played by the computer.
    """

    def __init__(self):
        self.code = None

    def make_code(self):
        self.code = get_random_code()

    def answer(self, guess):
        return compute_answer(guess, self.code)


class HumanCodeMaker(CodeMaker):
    """
    Implementation of Code Maker played by a human.
    """

    def __init__(self):
        self.code = None

    def make_code(self):
        self.code = get_code_from_user()

    def answer(self, guess):
        return get_answer_from_user(guess, self.code)


class HumanCodeBreaker(CodeBreaker):
    """
    Implementation of Code Breaker played by a human.
    """

    def initial_guess(self):
        return get_code_from_user()

    def guess(self, answer):
        return get_code_from_user()


class ComputerCodeBreaker(CodeBreaker):
    """
    Implementation of Code Breaker played by the computer.
    This implementation uses the Five-guess algorithm defined by Donald Knuth in 1977 as defined here:

        https://en.wikipedia.org/wiki/Mastermind_(board_game)

    This algorithm will always find the solution in at most five guesses.
    """

    def __init__(self):
        self._all_codes = list(itertools.product(COLORS, repeat=4))
        self._S = set(self._all_codes)
        self._last_guess = None

    def initial_guess(self):
        self._last_guess = 'AABB'
        return self._last_guess

    def guess(self, answer):
        guess = None

        # Filter possible candidates given the guess/answer
        self._S = set(filter(lambda c: compute_answer(self._last_guess, c) == answer, self._S))

        # Apply minimax strategy to optimize the next guess choice
        max_score = 0
        max_score_guesses = []
        for any_code in self._all_codes:
            hit_count = {}
            for code_candidate in self._S:
                answer = compute_answer(any_code, code_candidate)
                hit_count[answer] = hit_count.get(answer, 0) + 1
            score = len(self._S) - max(hit_count.values())
            if score > max_score:
                max_score = score
                max_score_guesses = [any_code]
            if score == max_score:
                max_score_guesses.append(any_code)

        # Prefer max score codes that are in S
        max_score_guesses_in_s = list(filter(lambda g: g in self._S, max_score_guesses))
        if max_score_guesses_in_s:
            guess = max_score_guesses_in_s[0]
        else:
            guess = max_score_guesses[0]

        self._last_guess = guess
        return self._last_guess


def play_game(code_maker, code_breaker):
    """
    Function handling a game session and the involved players.

    :param code_maker: A code maker player implementing the CodeMaker methods
    :param code_breaker: A code breaker player implementing the CodeBreaker methods
    :return: None
    """
    history = []

    print('[Code Maker]: Make a secret code')
    code_maker.make_code()

    print('[Code Breaker]: Make an initial guess')
    guess = code_breaker.initial_guess()
    print('[Code Breaker]: Initial guess is {}'.format(guess))

    while True:
        print('[Code Maker]: Give an answer')
        answer = code_maker.answer(guess)
        print('[Code Maker]: Answer is {}{}'.format(answer[0], answer[1]))

        history.append((guess, answer))
        print_history(history)

        if answer == (4, 0):
            print('[Code Breaker]: You broke the code!')
            print('[Code Breaker]: The code was: {}'.format(''.join(code_maker.code)))
            print('[Code Breaker]: Number of guesses: {}'.format(len(history)))
            break

        print('[Code Breaker]: Make a guess')
        guess = code_breaker.guess(answer)
        print('[Code Breaker]: Guess is {}'.format(''.join(guess)))


def get_code_from_user():
    """
    Read and validate the code given by a human player.

    :return: A valid code
    """
    while True:
        user_input = input('>>> ')
        if code_is_valid(user_input):
            return user_input
        else:
            print('Invalid input: Enter 4 symbols from "{}". e.g. AABB'.format(COLORS))


def get_answer_from_user(guess, code):
    """
    Read and validate the answer (of a guess) given by a human player.

    :param guess: The guess that needs an answer
    :param code: The code the guess is trying to match
    :return: A valid answer
    """
    while True:
        user_input = input('>>> ')
        if answer_is_valid(user_input, guess, code):
            return int(user_input[0]), int(user_input[1])
        else:
            print('Invalid input: Enter a valid (and correct) answer xx where x is a number. e.g. 02'.format(COLORS))


def code_is_valid(code):
    """
    Check whether the given code is valid.

    :param code: The string code to validate
    :return: True if the code is valid, False otherwise
    """
    return len(code) == 4 and not set(code) - set(COLORS)


def answer_is_valid(answer, guess, code):
    """
    Check whether the given answer is valid. The answer is also checked against
    the real answer derived from the given guess and code.

    :param answer: The answer to validate
    :param guess: The guess that has to be answered
    :param code: The code the guess is trying to match
    :return: True if the answer is valid, False otherwise
    """
    try:
        return len(answer) == 2 and (int(answer[0]), int(answer[1])) == compute_answer(guess, code)
    except ValueError:
        return False


def get_random_code():
    """
    Generate a random code of 4 colours.

    :return: A random code
    """
    return random.choices(COLORS, k=4)


def compute_answer(guess, code):
    """
    Given a guess and the code, return the number of black/white pegs according
    to the rules of mastermind.

    :param guess: The guess code
    :param code: The code to check against
    :return: A tuple representing the black/white pegs
    """
    black, white = 0, 0
    remained_guess, remained_code = [], []
    for i, symbol in enumerate(guess):
        if symbol == code[i]:
            black += 1
        else:
            remained_guess.append(symbol)
            remained_code.append(code[i])
    for color in remained_guess:
        if color in remained_code:
            white += 1
            remained_code.remove(color)
    return black, white


def print_history(history):
    """
    Print in a human readable way the guesses and the received answers.

    :param history: The list of the past guesses/answers
    :return: None
    """
    print()
    print('|====|=========|====|')
    for i in range(len(history)):
        print('|{:>3} | {} | {}{} |'.format(i + 1, ' '.join(history[i][0]), history[i][1][0], history[i][1][1]))
    print('|====|=========|====|')
    print()


def get_player_type_from_user(label, options):
    """
    Read the player from the user.

    :param label: the label of the player type
    :param options: the possible type options
    :return: the player type given by the user
    """
    while True:
        print('>>> Choose {} player type [{}]:'.format(label, '|'.join(options)))
        player_type = input('>>> ')
        if player_type.lower() in options:
            return player_type.lower()
        else:
            print('>>> Invalid type')


def main():
    """
    Main function.

    :return: None
    """
    try:
        print()
        print('======================')
        print('WELCOME TO MASTERMIND!')
        print('======================')
        print()
        print('[Hint]: The code is any sequence of four letters between A-F, e.g. ABCF)')
        print('[Hint]: The answer are two numbers, the number of correct letters in the right position '
              'and the number of correct letters in the wrong position')
        print()
        code_makers = {
            'cpu': ComputerCodeMaker,
            'human': HumanCodeMaker
        }
        code_breakers = {
            'cpu': ComputerCodeBreaker,
            'human': HumanCodeBreaker
        }
        while True:
            code_maker_type = get_player_type_from_user(label='Code Maker', options=['cpu', 'human'])
            code_breaker_type = get_player_type_from_user(label='Code Breaker', options=['cpu', 'human'])

            code_maker = code_makers[code_maker_type]()
            code_breaker = code_breakers[code_breaker_type]()

            play_game(code_maker, code_breaker)

            answer = input('>>> Game is over. Do you want to play again? [y|n]')
            if answer.lower() not in ['y', 'yes']:
                print('>>> Goodbye!')
                break

    except KeyboardInterrupt:
        print()
        print('>>> Goodbye!')


if __name__ == '__main__':
    main()
