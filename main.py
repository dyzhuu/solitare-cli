# Name: David Zhu
# UPI: dzhu292
import math
import random
import time
from enum import Enum

class Suit(Enum):
    CLUBS = "♣"
    DIAMONDS = "♢"
    HEARTS = "♡"
    SPADES = "♠"

class GameState(Enum):
    DEFAULT = 0
    WIN = 1
    RESET = 2
    QUIT = 3

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.hidden = True

    def __str__(self):
        """Returns the card as a string representation, either as a face down
        card, or the value of the card."""
        if self.hidden:
            return f"[*]"
        return f"{self.rank}{self.suit.value}"

    def __format__(self, format_spec):
        """Returns the formatted string"""
        if self.hidden:
            return f"{'[*]':{format_spec}}"
        return f"{str(self.rank) + self.suit.value:{format_spec}}"

    def is_red(self):
        """Returns true if the card is red, false otherwise"""
        return self.suit in [Suit.HEARTS, Suit.DIAMONDS]

    def is_black(self):
        """Returns true if the card is black, false otherwise"""
        return self.suit in [Suit.CLUBS, Suit.SPADES]

class CardPile:
    def __init__(self):
        self.items = []

    def __eq__(self, other):
        """Returns true if the items are the same and of the same class,
        false otherwise"""
        if not isinstance(other, type(self)):
            return False
        if self.items == other.items:
            return True
        return False

    def add_top(self, item):
        """Adds a card to top of the pile"""
        self.items.append(item)

    def remove_top(self):
        """Removes a card from the top of the pile"""
        return self.items.pop()

    def cut(self, number):
        """Returns x number of cards from the top of the pile"""
        cut_items = self.items[-number:]
        self.items = self.items[:-number]
        return cut_items

    def extend(self, items):
        """Adds multiple cards to the top of the pile"""
        self.items.extend(items)

    def size(self):
        """Returns the number of cards in the pile"""
        return len(self.items)

    def is_empty(self):
        """Returns true if pile is empty, false otherwise"""
        return self.size() == 0

    def peek(self, number=1):
        """Returns the top card"""
        return self.items[-number]

    def formatted(self, padding):
        """Returns a list of fixed size padded with empty strings"""
        if self.size() == 0:
            return [''] * padding
        return self.items + [''] * (padding - self.size())

class Solitaire:
    # spacing of 15 characters between every pile on the display
    WIDTH = 15

    def __init__(self, max_rank=13):
        self.stock = CardPile()
        self.waste = CardPile()
        self.foundations = {suit: CardPile() for suit in Suit}
        self.num_cards = 4 * max_rank
        self.max_rank = max_rank
        self.num_piles = math.floor(math.sqrt(self.num_cards))
        self.piles = [CardPile() for _ in range(self.num_piles)]
        self.move_number = 1
        self.history = []
        self.game_state = GameState.DEFAULT
        # creates a deck of 4 suits from 1 to max_rank
        deck = [Card(rank, suit) for suit in Suit for rank in
                range(1, self.max_rank + 1)]
        random.shuffle(deck)
        # adds card to their piles in a staircase pattern
        for pile in range(self.num_piles):
            for _ in range(pile + 1):
                self.piles[pile].add_top(deck.pop())
            self.piles[pile].peek().hidden = False
        for card in deck:
            card.hidden = False
        self.stock.extend(deck)

    @staticmethod
    def is_valid_move(card1: Card, card2: Card):
        """Returns true if card2 can be placed on card 1, false otherwise"""
        if card1.hidden:
            return False
        if card1.is_red() and card2.is_red():
            return False
        if card1.is_black() and card2.is_black():
            return False
        if card1.rank != card2.rank - 1:
            return False
        return True

    @staticmethod
    def display_instructions():
        """Prints instructions"""
        print(" USAGE INSTRUCTIONS ".center(100, '_'))
        print("""
        >> 'd' to draw from the stock pile
        >> 'u' or 'z' to undo the last move
        >> 'i' to view this screen again
        >> 'reset' to start a new game
        >> 'quit' to quit
        
        The first move is the card pile to move from
        The second move is the card pile to move to

        i.e.
        >> x
        >> y
        moves a card from pile x to pile y
        
        SPECIAL CODES
        <number> represents the respective numbered pile
        'w' represents the waste pile
        'f' represents the foundation pile
        (use f<number> when moving from the foundation pile)
        
        example: 
        >> 1
        >> 2 (moves card from pile 1 to pile 2)

        >> w        
        >> 1 (moves card from waste to pile 1)

        >> 1
        >> f (moves card from pile 1 to the foundation of the respective suit)

        >> f2
        >> 1 (moves card from foundation 2 to pile 1)
        
        To move multiple cards from from one pile to another, enter m<number>
        example:
        >> m3
        >> 1
        >> 2 (moves the bottom 3 cards from pile 1 to pile 2

        Referenced from https://bicyclecards.com/how-to-play/solitaire\n""")
        input('PRESS "ENTER" TO START GAME')

    def display(self):
        """Prints the main display"""
        print("STOCK".ljust(self.WIDTH)
              + "WASTE".ljust(self.WIDTH)
              + ' ' * (self.num_piles - 6) * self.WIDTH, end="")
        for i in range(4):
            print(f"FOUNDATION {i + 1}".ljust(self.WIDTH), end="")
        print()
        print(f"{'[*]' if not self.stock.is_empty() else '_':<{self.WIDTH}}",
              end="")
        if self.waste.is_empty():
            print('_'.ljust(self.WIDTH), end="")
        else:
            print(f'{self.waste.peek():<{self.WIDTH}}', end="")
        print(' ' * (self.num_piles - 6) * self.WIDTH, end="")
        for suit in self.foundations:
            if self.foundations[suit].is_empty():
                print('_'.ljust(self.WIDTH), end="")
            else:
                print(f"{self.foundations[suit].peek():<{self.WIDTH}}", end="")
        print()
        print("({} card{})"
              .format(self.stock.size(), '' if self.stock.size() == 1 else 's')
              .ljust(self.WIDTH), end="")
        print(f"({self.waste.size()} "
              f"card{'' if self.waste.size() == 1 else 's'})".ljust(self.WIDTH)
              + ' ' * ((self.num_piles - 6) * self.WIDTH), end="")
        for suit in self.foundations:
            print("({} card{})"
                  .format(self.foundations[suit].size(),
                          '' if self.foundations[suit].size() == 1 else 's')
                  .ljust(self.WIDTH), end="")
        print()
        print(" TABLEAU ".center(self.num_piles * self.WIDTH, '_'))
        for column in range(1, self.num_piles + 1):
            print(f"{'Pile ' + str(column):<{self.WIDTH}}", end="")
        print()
        longest_pile_length = max(map(lambda pile: len(pile.items), self.piles))

        columns = zip(*[self.piles[column].formatted(longest_pile_length)
                        for column in range(self.num_piles)])
        for column in columns:
            for card in column:
                print(f'{card:<{self.WIDTH}}', end="")
            print()
        print("", end="")
        for pile in self.piles:
            print(f"({pile.size()} "
                  f"card{'' if pile.size() == 1 else 's'})".ljust(self.WIDTH),
                  end="")
        print()
        for pile in self.piles:
            num_revealed = len(list(
                filter(lambda card: not card.hidden, pile.items)))
            print(f"({num_revealed} shown)".ljust(self.WIDTH), end="")
        print()

    def draw(self):
        """Draws a card from the stock onto the waste, if stock
        is empty, returns all cards from waste onto stock."""
        if self.stock.is_empty():
            self.stock.extend(reversed(self.waste.cut(self.waste.size())))
        else:
            self.waste.add_top(self.stock.remove_top())

    def move(self, origin_pile, destination_pile, num_cards=1):
        """Moves x cards from the origin pile to the destination pile"""
        if origin_pile.size() < num_cards:
            return
        if origin_pile == destination_pile:
            return
        if (destination_pile.is_empty()
                and origin_pile.peek(num_cards).rank == self.max_rank):
            destination_pile.extend(origin_pile.cut(num_cards))
        elif self.is_valid_move(origin_pile.peek(num_cards),
                                destination_pile.peek()):
            destination_pile.extend(origin_pile.cut(num_cards))
        else:
            return False
        if not origin_pile.is_empty():
            self.history.append((origin_pile, destination_pile,
                                 num_cards, origin_pile.peek().hidden))
            origin_pile.peek().hidden = False
        else:
            self.history.append((origin_pile, destination_pile,
                                 num_cards, False))

    def move_to_foundation(self, pile):
        """Moves a single card from a pile to the foundation"""
        if pile.is_empty():
            return
        suit = pile.peek().suit
        if self.foundations[suit].is_empty() and pile.peek().rank == 1:
            self.foundations[suit].add_top(pile.remove_top())
        elif (not self.foundations[suit].is_empty()
                and self.foundations[suit].peek().rank == pile.peek().rank - 1):
            self.foundations[suit].add_top(pile.remove_top())
        else:
            return False
        if not pile.is_empty():
            self.history.append((pile, self.foundations[suit],
                                 1, pile.peek().hidden))
            pile.peek().hidden = False
        else:
            self.history.append((pile, self.foundations[suit], 1, False))
        return True

    def undo(self):
        """Undoes the most recent move"""
        if not self.history:
            return
        last_move = self.history.pop()
        if last_move == "d" and self.waste.is_empty():
            self.waste.extend(reversed(self.stock.cut(self.stock.size())))
            return
        elif last_move == "d" and not self.waste.is_empty():
            self.stock.add_top(self.waste.remove_top())
            return
        origin_pile, destination_pile, num_cards, hidden = last_move
        if hidden:
            origin_pile.peek().hidden = True
        origin_pile.extend(destination_pile.cut(num_cards))

    def is_complete(self):
        """Returns true if game is complete, i.e. stock and waste is empty, and
        there are no more hidden cards"""
        if not self.stock.is_empty():
            return False
        if not self.waste.is_empty():
            return False
        # returns false if there still exists hidden cards on the tableau
        hidden_cards = []
        for pile in self.piles:
            hidden_cards.extend(list(filter(lambda x: x.hidden, pile.items)))
        if hidden_cards:
            return False
        return True

    def process_input(self):
        """Function for parsing user input and determining the correct action"""
        pile1 = input("Enter your first move: ").strip().lower()
        if pile1 == "reset":
            self.game_state = GameState.RESET
            return
        if pile1 == "quit":
            self.game_state = GameState.QUIT
            return
        if pile1.startswith("i"):
            self.display_instructions()
            raise ValueError("Move not processed")
        if pile1 == "d":
            self.draw()
            self.history.append('d')
            return
        elif pile1 == "u" or pile1 == "z":
            self.undo()
            return
        if pile1.startswith("m"):
            num_cards = int(pile1[1:])
            pile1 = int(input("Enter pile to remove the card from: "))
            pile2 = int(input("Enter pile to move the card to: "))
            if 1 <= pile1 <= self.num_piles and 1 <= pile2 <= self.num_piles:
                self.move(self.piles[pile1 - 1],
                          self.piles[pile2 - 1], num_cards)
            return
        if not pile1.startswith('f') and not pile1.isdigit() and pile1 != "w":
            raise ValueError('Improper input')
        pile2 = input("Enter your second move: ").strip().lower()
        if not pile2.isdigit() and pile2 != "f":
            raise ValueError('Improper input')
        if pile1.startswith("f") and 1 <= int(pile2) <= self.num_piles:
            foundation_num = int(pile1[1:])
            suit = list(self.foundations)[foundation_num - 1]
            if 1 <= foundation_num <= 4:
                self.move(self.foundations[suit], self.piles[int(pile2) - 1])
            else:
                raise ValueError('Improper input')
        elif pile1 == "w" and pile2 == 'f':
            self.move_to_foundation(self.waste)
        elif pile1 == "w" and 1 <= int(pile2) <= self.num_piles:
            self.move(self.waste, self.piles[int(pile2) - 1])
        elif pile2 == "f" and 1 <= int(pile1) <= self.num_piles:
            self.move_to_foundation(self.piles[int(pile1) - 1])
        elif (1 <= int(pile1) <= self.num_piles
                and 1 <= int(pile2) <= self.num_piles):
            self.move(self.piles[int(pile1) - 1], self.piles[int(pile2) - 1])
        else:
            raise ValueError('Improper input')

    def play(self):
        """Starts the game"""
        while not self.is_complete() and self.game_state == GameState.DEFAULT:
            num_moves = len(self.history)
            self.display()
            print()
            print(f"Round {self.move_number}"
                  .center(self.num_piles * self.WIDTH, '_'))
            try:
                self.process_input()
            except (ValueError, IndexError):
                pass
            # increments if a valid move has been made (history changed)
            if len(self.history) != num_moves:
                self.move_number += 1

        # Returns game state for game class to handle, not default implies
        # either quit or reset.
        if self.game_state != GameState.DEFAULT:
            return self.game_state

        # Otherwise if won, returns all cards to foundation
        while list(filter(lambda pile: not pile.is_empty(), self.piles)):
            for pile in reversed(self.piles):
                if self.move_to_foundation(pile):
                    time.sleep(0.1)
                    self.display()
        print("\nYou Win in", self.move_number - 1, "steps!\n")
        return GameState.WIN

class Game:
    def __init__(self):
        self.game = None

    def initialise_game(self):
        """Initialises an instance of the Solitare game"""
        self.game = Solitaire(13)

    def start(self):
        """Starts a game session, where you can play multiple Solitare games"""
        Solitaire.display_instructions()
        result = None
        while result != GameState.QUIT:
            self.initialise_game()
            result = self.game.play()
            if (result == GameState.WIN
                    and input("Play again? (Y/N): ").lower().strip() != "y"):
                return


game = Game()
game.start()
