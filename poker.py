from card import Deck
from collections import Counter
from operator import itemgetter
import random

class Poker:
    def __init__(self):
        self._game_deck = Deck()
        
    @property
    def game_deck(self):
        return self._game_deck
        
    def start_game(self, players):
        self._game_deck.shuffle()
        self.give_money(players)
        self.play_round(players)
    
    def play_round(self, players):
        self.hole_cards(players)
        self.the_flop(players)
        self.the_turn(players)
        self.the_river(players)
        self.check_hand(players)
    
    def give_money(self, players):
        self.wallet = []
        for money in range(players):
            self.wallet.append(500)
        
    def hole_cards(self, players):
        self.player_hands = [[self._game_deck.cards[cards + ((hand)*3)] for cards in range(2)] for hand in range(players) ]
    
    def the_flop(self, players):
        self.community_cards = [self._game_deck.cards[cards + (players*3)] for cards in range(3)]
            
    def the_turn(self, players):
        self.community_cards.append(self._game_deck.cards[(players*3) + 3])

    def the_river(self, players):
        self.community_cards.append(self._game_deck.cards[(players*3) + 4])
        
    def check_hand(self, players):
        self.combined_hand = self.player_hands[0] + self.community_cards
        self.combined_suit = [card.suit for card in self.combined_hand]
        self.combined_number = [card.number for card in self.combined_hand]
        self.combined_value = [card.value for card in self.combined_hand]
        self.value_counter = Counter(self.combined_value)
        
        sorted_value_counter = sorted(self.value_counter.items(), reverse=True)
        self.suit_counter = Counter(self.combined_suit)
        max_value = max(sorted_value_counter, key=itemgetter(1))
        
        max_value_counter = Counter(self.value_counter.values())
        
        max_suit = max(self.suit_counter, key=self.suit_counter.get)
        
        # checks straight and high card
        sorted_values = sorted(set(self.combined_value))
        gaps = [[s, e] for s, e in zip(sorted_values, sorted_values[1:]) if s+1 < e]
        edges = iter(sorted_values[:1] + sum(gaps, []) + sorted_values[-1:])
        card_ranges = list(zip(edges, edges))
        straight_check = [consecutive_cards[1] - consecutive_cards[0] for consecutive_cards in card_ranges]
        if any(value > 3 for value in straight_check):
            straight_high = 5
            for highs in card_ranges:
                if highs[1] - highs[0] > 3:
                    straight_high = highs[1]
                    
        if any(value > 4 for value in self.suit_counter.values()) and any(value > 3 for value in straight_check):
            hand_value = 'Straight Flush'
        elif max_value_counter[max_value_counter[4] > 0] > 0:
            hand_value = 'Four of a Kind of ' + str(max_value[0])
        elif max_value_counter[3] > 0 and max_value_counter[2] > 0:
            hand_value = 'Full House'
        elif any(value > 4 for value in self.suit_counter.values()):
            hand_value = max_suit + ' Flush'
        elif any(value > 3 for value in straight_check):
            hand_value = str(straight_high) + ' High Straight'
        elif max_value_counter[3] > 0:
            hand_value = 'Three of a Kind of ' + str(max_value[0])
        elif max_value_counter[2] > 1:
            hand_value = 'Two Pair'
        elif max_value_counter[2] > 0:
            hand_value = 'One Pair of ' + str(max_value[0])
        else:
            hand_value = str(max_value[0]) + ' High Card'
        
        print(hand_value)
            
game = Poker()
game.start_game(5)
print(game.combined_hand)
print(list(game.suit_counter.values()))
print(list(game.value_counter.values()))