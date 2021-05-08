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
        self.players = players
        self.give_money()
        for x in range(4):
            self._game_deck.shuffle()
            self.play_round()
    
    def play_round(self):
        self.in_play = [True for check in range(self.players)]
        self.jackpot = 0
        self.hole_cards()
        self.check_players()
        self.turn_decision()
        print('Current pot: ' + str(self.jackpot))
        self.the_flop()
        self.check_players()
        self.turn_decision() 
        print('Current pot: ' + str(self.jackpot))
        self.the_turn()
        self.check_players()
        self.turn_decision() 
        print('Current pot: ' + str(self.jackpot))
        self.the_river()
        self.check_players()
        self.turn_decision()
        print('current pot: ' + str(self.jackpot))
        self.check_hand()
    
    def give_money(self):
        self.wallet = []
        for money in range(self.players):
            self.wallet.append(500)

    def turn_decision(self):
        bet_raised = [False for bets in range(self.players)]
        bet_raiser = self.players
        while all(bet_raised) != True:
            for player_turn in range(self.players):
                if self.in_play[player_turn] == False:
                    bet_raised[player_turn] = True
                    self.players_current_bet[player_turn] = self.current_bet
                
                valid = False

                while valid == False and self.in_play[player_turn] == True and bet_raised[player_turn] == False:
                    decision = input('Player ' + str(player_turn+1) + ': check, call, raise, or fold? ')
                    if decision == 'check':
                        if self.players_current_bet[player_turn-1] == self.players_current_bet[player_turn]:
                            self.check(player_turn)
                            bet_raised[player_turn] = True
                            valid = True
                        else:
                            print('Cannot check with current bet of ' + str(self.current_bet))
                    elif decision == 'call':
                        if self.current_bet < self.wallet[player_turn]:
                            if self.players_current_bet[player_turn] < self.current_bet:
                                self.call_bet(player_turn)
                                bet_raised[player_turn] = True
                                valid = True
                                raise_check = all(bets == self.current_bet for bets in self.players_current_bet)
                                if raise_check == True:
                                    bet_raised[bet_raiser] = True
                            elif self.players_current_bet[player_turn] == self.current_bet:
                                print('You cannot call your own bet of ' + str(self.current_bet))
                        else:
                            print('Insufficent funds')
                    elif decision == 'raise':
                        amount = int(input('Bet amount?: '))
                        if amount < self.wallet[player_turn]:
                            if amount > self.current_bet:
                                self.raise_bet(player_turn, amount)
                                bet_raised = [False for bets in range(self.players)]
                                bet_raiser = player_turn
                                valid = True
                            else:
                                print('Raise must be greater than current bet of ' + str(self.current_bet))
                        else:
                            print('Insufficient funds')
                    elif decision == 'fold':
                        self.fold(player_turn)
                        bet_raised[player_turn] = True
                        self.players_current_bet[player_turn] = self.current_bet
                        valid = True


    def check_players(self):
        self.players_current_bet = [0 for players in range(self.players)]

    def bet(self, player, amount):
        print('Player ' + str(player+1) + ' bet ' + str(amount))
        amount = input('Enter your bet: ')
        self.wallet[player-1] -= amount
        self.current_bet = amount
        self.jackpot += amount

    def check(self, player):
        print('Player ' + str(player+1) + ' checked')

    def raise_bet(self, player, amount):
        print('Player ' + str(player+1) + ' raised bet from ' + str(self.current_bet) + ' to ' + str(amount))
        self.players_current_bet[player] = amount
        self.wallet[player-1] -= amount
        self.current_bet = amount
        self.jackpot += amount

    def call_bet(self, player):
        print('Player ' + str(player+1) + ' called bet of ' + str(self.current_bet))
        self.players_current_bet[player] = self.current_bet
        self.wallet[player-1] -= self.current_bet
        self.jackpot += self.current_bet

    def fold(self, player):
        print('Player ' + str(player+1) + ' folded')
        self.in_play[player] = False
        
    def hole_cards(self):
        self.current_bet = 0
        self.player_hands = [[self._game_deck.cards[cards + ((hand)*3)] for cards in range(2)] for hand in range(self.players)]
        for hand in self.player_hands:
            print(hand)
    
    def the_flop(self):
        self.current_bet = 0
        self.community_cards = [self._game_deck.cards[cards + (self.players*3)] for cards in range(3)]
        print(self.community_cards)
            
    def the_turn(self):
        self.current_bet = 0
        self.community_cards.append(self._game_deck.cards[(self.players*3) + 3])
        print(self.community_cards)

    def the_river(self):
        self.current_bet = 0
        self.community_cards.append(self._game_deck.cards[(self.players*3) + 4])
        print(self.community_cards)
        
    def check_hand(self):
        self.hand_values = [(0, 0) for hands in range(self.players)]
        for player in range(self.players):
            # player's hold cards + community cards
            self.combined_hand = self.player_hands[player] + self.community_cards

            # lists of suit and value 
            combined_suit = [card.suit for card in self.combined_hand]
            combined_value = [card.value for card in self.combined_hand]

            # counts the number of same valued cards
            value_counter = Counter(combined_value)

            # sorts the list of same valued cards by value to get the high card
            sorted_value_counter = sorted(value_counter.items(), reverse=True)

            # finds the high card
            max_value = max(sorted_value_counter, key=itemgetter(1))

            # removes the max value from the list and finds the second highest value
            second_sorted_value_counter = sorted_value_counter
            second_sorted_value_counter.remove(max_value)
            second_max_value = max(second_sorted_value_counter, key=itemgetter(1))

            # counts the number of singles, pairs, triples, and quadruples there are
            max_value_counter = Counter(value_counter.values())
         
            # counts the number of cards from the same suit
            suit_counter = Counter(combined_suit)
            # gets the suit with the most cards
            max_suit = max(suit_counter, key=suit_counter.get)

            # checks for straight flush, flush high, and royal flush
            straight_flush_check = []
            if any(value > 4 for value in suit_counter.values()):
                for card in self.combined_hand:
                    if card.suit == max_suit:
                        straight_flush_check.append(card)
                flush_high = [card.number for card in straight_flush_check]
                flush_high = max(flush_high)
            straight_flush_high = self.straight_check([card.value for card in straight_flush_check])
        
            # checks for straights and the high card
            straight_high = self.straight_check(combined_value)

            # converts face card value to name
            if max_value[0] in [14]:
                max_value = ('Ace', max_value[1])
            elif max_value[0] in [13]:
                max_value = ('King', max_value[1])
            elif max_value[0] in [12]:
                max_value = ('Queen', max_value[1])
            elif max_value[0] in [11]:
                max_value = ('Jack', max_value[1])
            if second_max_value[0] in [14]:
                second_max_value = ('Ace', second_max_value[1])
            elif second_max_value[0] in [13]:
                second_max_value = ('King', second_max_value[1])
            elif second_max_value[0] in [12]:
                second_max_value = ('Queen', second_max_value[1])
            elif second_max_value[0] in [11]:
                second_max_value = ('Jack', second_max_value[1])
                    
            # checks what the hand is in descending order of values of hands
            if any(value > 4 for value in suit_counter.values()) and straight_flush_high == 'Ace':
                hand_value = 'ROYAL FLUSH, ' + max_suit + ' **************************************************************************************'
                self.hand_values[player] = (9, 'A')
            elif any(value > 4 for value in suit_counter.values()) and straight_flush_high is not None:
                hand_value = str(straight_flush_high) + ' High Straight Flush, ' + max_suit + ' **************************************************************************************'
                self.hand_values[player] = (8, straight_flush_high)
            elif max_value_counter[max_value_counter[4] > 0] > 0:
                hand_value = 'Four of a Kind, ' + str(max_value[0]) + 's'
                self.hand_values[player] = (7, max_value[0])
            elif max_value_counter[3] > 0 and max_value_counter[2] > 0:
                hand_value = 'Full House, ' + str(max_value[0]) + 's over ' + str(second_max_value[0])
                self.hand_values[player] = (6, max_value[0], second_max_value[0])
            elif any(value > 4 for value in suit_counter.values()):
                hand_value =  str(flush_high) + ' High Flush, ' + max_suit
                self.hand_values[player] = (5, flush_high)
            elif straight_high is not None:
                hand_value = str(straight_high) + ' High Straight'
                self.hand_values[player] = (4, straight_high)
            elif max_value_counter[3] > 0:
                hand_value = 'Three of a Kind, ' + str(max_value[0]) + 's'
                self.hand_values[player] = (3, max_value[0])
            elif max_value_counter[2] > 1:
                hand_value = 'Two Pair, ' + str(max_value[0]) + 's and ' + str(second_max_value[0]) + 's'
                self.hand_values[player] = (2, max_value[0], second_max_value[0])
            elif max_value_counter[2] > 0:
                hand_value = 'One Pair, ' + str(max_value[0]) + 's'
                self.hand_values[player] = (1, max_value[0])
            else:
                hand_value = 'High Card, ' + str(max_value[0])
                self.hand_values[player] = (0, max_value[0])

            print(hand_value)

    def straight_check(self, nums):
        # checks straight with high card
        nums = sorted(set(nums))
        gaps = [[s, e] for s, e in zip(nums, nums[1:]) if s+1 < e]
        edges = iter(nums[:1] + sum(gaps, []) + nums[-1:])
        card_ranges = list(zip(edges, edges))
        check_straight = [consecutive_cards[1] - consecutive_cards[0] for consecutive_cards in card_ranges]
        if any(value > 3 for value in check_straight):
            straight_high = 5
            for highs in card_ranges:
                if highs[1] - highs[0] > 3:
                    straight_high = highs[1]
                    if straight_high in [14]:
                        straight_high = 'Ace'
                    elif straight_high in [13]:
                        straight_high = 'King'
                    elif straight_high in [12]:
                        straight_high = 'Queen'
                    elif straight_high in [11]:
                        straight_high = 'Jack'
            return straight_high

check = '' 
count = 0
while check == '':
    game = Poker()
    game.start_game(3)
    print(game.combined_hand)
    count += 1
    print(count)
    #check = input()