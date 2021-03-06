from card import Deck
from collections import Counter
from operator import itemgetter
from win32api import GetSystemMetrics
from graphics import *
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
        # initialize the graphics
        self.initial_graphics()
        # checks to see if anyone still has money other than the richest player
        self.check_balances()
        # continue until one player has all the money
        while self.players_with_cash:
            # shuffle the game deck
            self._game_deck.shuffle()
            # play a round
            self.play_round()
            # check everyone's balance again
            self.check_balances()
        # ends the game once one player has all the money
        self.end_game()
    
    def play_round(self):
        self.exit_loop = 0
        # sets everyone as in play until they fold
        self.in_play = [True for check in range(self.players)]
        # sets the round's jackpot to 0
        self.jackpot = 0
        self.update_jackpot_text()
        # deals the hole cards to each player
        self.hole_cards()
        # sets everyone's current bets to 0
        self.check_players()
        # gets player's decision
        self.turn_decision()
        self.update_jackpot_text()
        self.update_balances_text()
        print('Current pot: $' + str(self.jackpot))
        # deals the flop to the table
        self.the_flop()
        # sets everyone's current bets to 0
        self.check_players()
        # gets player's decision
        self.turn_decision() 
        self.update_jackpot_text()
        self.update_balances_text()
        print('Current pot: $' + str(self.jackpot))
        # deals the turn to the table
        self.the_turn()
        # sets everyone's current bets to 0
        self.check_players()
        # gets player's decision
        self.turn_decision() 
        self.update_jackpot_text()
        self.update_balances_text()
        print('Current pot: $' + str(self.jackpot))
        # deals the river to the table
        self.the_river()
        # sets everyone's current bets to 0
        self.check_players()
        # gets player's decision
        self.turn_decision()
        self.update_jackpot_text()
        self.update_balances_text()
        print('current pot: $' + str(self.jackpot))
        # checks everyone's hand and calculates the best hand
        self.check_hand()
        # compares everyone that is in play's hand to each other and then decides the winning hand
        self.compare_hand()
        # presents the winning player and pays them unless there is a tie, then distributes evenly
        if self.winning_player[0] != -1:
            # if there are more than 1 winning player then distribute evenly
            if len(self.winning_player) > 1:
                winning_player_string = ', '.join([str(player) for player in self.winning_player])
                print('Winning Hand: Players ' + winning_player_string)
                self.update_player_action_text('Winning Hand: Players ' + winning_player_string)
                for payout in self.winning_player:
                    self.wallet[payout-1] += self.jackpot/len(self.winning_player)
            # else there is 1 winning player and they get it all
            else:
                print('Winning Hand: Player ' + str(self.winning_player[0]))
                self.update_player_action_text('Winning Hand: Player ' + str(self.winning_player[0]))
                self.wallet[self.winning_player[0]-1] += self.jackpot
        # if everyone folds then no player is left in play
        else:
            print('No player left in play')
            self.update_player_action_text('No player left in play')
        # shows all the hole cards of every player
        for players in range(self.players):
            self.show_hole_cards(players)
            self.show_hand_text(players)
        # update text for balances
        self.update_balances_text()
        if self.exit_loop == 1:
            self.win.getMouse()
        # pause
        self.win.getMouse()
        # hide all the hole cards of every player
        for players in range(self.players):
            self.hide_hole_cards(players)
            self.hide_hand_text(players)
        # hide the community cards
        self.hide_community_cards()
    
    def give_money(self):
        # gives everyone $500
        self.wallet = []
        for money in range(self.players):
            self.wallet.append(500)

    def check_balances(self):
        # makes a list of everyone's balances and then removes the player with the most money and checks if other players still have money
        balances = [money for money in self.wallet]
        max_balance = max(balances)
        balances.remove(max_balance)
        overall_balances = [True for players in balances if players > 0]
        self.players_with_cash = any(overall_balances)

    def turn_decision(self):
        # makes a list for every player to check to see if someone raised the bet
        bet_raised = [False for bets in range(self.players)]
        # sets the person who raised the bet as the last player
        bet_raiser = self.players
        # while all players are not matching the current bets, ask every player for the decision
        while all(bet_raised) != True:
            # loops through all the players
            for player_turn in range(self.players):
                # if the player has folded then set everything to true to skip their turn
                if self.in_play[player_turn] == False:
                    bet_raised[player_turn] = True
                    self.players_current_bet[player_turn] = self.current_bet
                
                # valid input check value until user inputs a correct input
                valid = False

                # show the back of the cards until 'show cards' is clicked
                self.show_back_cards(player_turn)

                # while the player's move is still not valid, they are still in play, and they were not the player to raise the bet then ask for their input until they select a valid input
                while valid == False and self.in_play[player_turn] == True and bet_raised[player_turn] == False:
                    # display the player's current balance
                    print('Player ' + str(player_turn+1) + ': $' + str(self.wallet[player_turn]))
                    self.update_current_bet_text()
                    #decision = input('Player ' + str(player_turn+1) + ': check, call, raise, or fold? ')
                    # gets the input of clicking the graphic
                    decision = self.get_input()
                    #decision = 'check' # used to speedily move through hands for testing purposes
                    if decision == 'check':
                        # if the current bet of the player before is equal to the current bet of the current player then set everything to true to move on to the next player
                        if self.players_current_bet[player_turn-1] == self.players_current_bet[player_turn]:
                            self.check(player_turn)
                            bet_raised[player_turn] = True
                            valid = True
                        # if the current bets are not equal, then they must call or raise or fold
                        else:
                            print('Cannot check with current bet of $' + str(self.current_bet))
                            self.update_player_action_text('Cannot check with current bet of $' + str(self.current_bet))
                    elif decision == 'call':
                        # if the player has enough money in their balance to call then match the current bet
                        if self.current_bet <= self.wallet[player_turn]:
                            # if the player's current bet is less than the current bet of the table then increase their bet to match
                            if self.players_current_bet[player_turn] < self.current_bet:
                                self.call_bet(player_turn)
                                bet_raised[player_turn] = True
                                valid = True
                                # checks to see if all the players have the same bet and if so, then marks everyone as raised to move to the next round
                                raise_check = all(bets == self.current_bet for bets in self.players_current_bet)
                                if raise_check == True:
                                    bet_raised[bet_raiser] = True
                            # if the player's current bet is equal to the current bet of the table then they must raise or fold
                            elif self.players_current_bet[player_turn] == self.current_bet:
                                print('You cannot call your own bet of $' + str(self.current_bet))
                                self.update_player_action_text('You cannot call your own bet of $' + str(self.current_bet))
                        # if the player doesn't have enough money in their balance to call then they must check or fold
                        else:
                            print('Insufficent funds')
                            self.update_player_action_text('Insufficent funds')
                    elif decision == 'raise':
                        # asks for bet amount
                        self.update_player_action_text('Bet amount?: $')
                        # amount = int(input('Bet amount?: $'))
                        try:
                            amount = int(self.get_keyboard())
                        except:
                            amount = 0
                        # if the player has enough money in their balance to raise to that amount
                        if amount <= self.wallet[player_turn]:
                            # if the amount is greater than the current bet of the table then raise the bet
                            if amount > self.current_bet:
                                self.raise_bet(player_turn, amount, 0)
                                bet_raised = [False for bets in range(self.players)]
                                bet_raiser = player_turn
                                valid = True
                            # if the player's bet is not higher than the current bet then they must enter a higher bet
                            else:
                                print('Raise must be greater than current bet of $' + str(self.current_bet))
                                self.update_player_action_text('Raise must be greater than current bet of $' + str(self.current_bet))
                        # if the player doesn't have enough money in their balance to raise then they must lower the raise or check or fold or call
                        else:
                            print('Insufficient funds')
                            self.update_player_action_text('Insufficent funds')
                    elif decision == 'all in':
                        # set the bet amount to the rest of the players wallet
                        amount = self.wallet[player_turn]
                        # if the player has enough money in their balance to raise to that amount
                        if amount <= self.wallet[player_turn]:
                            # if the amount is greater than the current bet of the table then raise the bet
                            if amount >= self.current_bet:
                                self.raise_bet(player_turn, amount, 1)
                                bet_raised = [False for bets in range(self.players)]
                                bet_raiser = player_turn
                                valid = True
                            # if the player's bet is not higher than the current bet then they must enter a higher bet
                            else:
                                print('Raise must be greater than current bet of $' + str(self.current_bet))
                                self.update_player_action_text('Raise must be greater than current bet of $' + str(self.current_bet))
                        # if the player doesn't have enough money in their balance to raise then they must lower the raise or check or fold or call
                        else:
                            print('Insufficient funds')
                            self.update_player_action_text('Insufficent funds')
                    elif decision == 'fold':
                        # sets the player as not in play
                        self.fold(player_turn)
                        bet_raised[player_turn] = True
                        self.players_current_bet[player_turn] = self.current_bet
                        valid = True
                    elif decision == 'show cards' and self.showing_cards == False:
                        # shows the hole cards
                        self.show_hole_cards(player_turn)
                        self.hide_back_cards(player_turn)
                    elif decision == 'show cards' and self.showing_cards == True:
                        # hides the hole cards
                        self.hide_hole_cards(player_turn)
                        self.show_back_cards(player_turn)

                # if the cards are showing, hide them, else hide the back cards
                if self.showing_cards == True:
                    self.hide_hole_cards(player_turn)
                else:
                    self.hide_back_cards(player_turn)

    def check_players(self):
        # set the current bet for all players to 0
        self.players_current_bet = [0 for players in range(self.players)]

    def check(self, player):
        # displays that the player checked
        print('Player ' + str(player+1) + ' checked')
        self.update_player_action_text('Player ' + str(player+1) + ' checked')

    def raise_bet(self, player, amount, all_in):
        # displays that the player raised
        if all_in == 0:
            print('Player ' + str(player+1) + ' raised bet from $' + str(self.current_bet) + ' to $' + str(amount))
            self.update_player_action_text('Player ' + str(player+1) + ' raised bet from $' + str(self.current_bet) + ' to $' + str(amount))
        if all_in == 1:
            print('Player ' + str(player+1) + ' is all in with $' + str(amount))
            self.update_player_action_text('Player ' + str(player+1) + ' is all in with $' + str(amount))
        # adds back the player's last bet back to their balance
        self.wallet[player] += self.players_current_bet[player]
        # removes the previous bet from the jackpot
        self.jackpot -= self.players_current_bet[player]
        # sets the player's current bet to the amount
        self.players_current_bet[player] = amount
        # subtracts the amount from the wallet
        self.wallet[player] -= amount
        # sets the current bet of the table to the amount
        self.current_bet = amount
        # adds the amount to the jackpot
        self.jackpot += amount

    def call_bet(self, player):
        # displays that the player called
        print('Player ' + str(player+1) + ' called bet of $' + str(self.current_bet))
        self.update_player_action_text('Player ' + str(player+1) + ' called bet of $' + str(self.current_bet))
        # adds back the player's last bet back to their balance
        self.wallet[player] += self.players_current_bet[player]
        # removes the previous bet from the jackpot
        self.jackpot -= self.players_current_bet[player]
        # changes the current player's bet to match the current bet of the table
        self.players_current_bet[player] = self.current_bet
        # subtracts the current bet of the table from the wallet
        self.wallet[player] -= self.current_bet
        # adds the amount to the jackpot
        self.jackpot += self.current_bet

    def fold(self, player):
        # displays that the player folded
        print('Player ' + str(player+1) + ' folded')
        self.update_player_action_text('Player ' + str(player+1) + ' folded')
        # sets the player to not in play
        self.in_play[player] = False
        
    def hole_cards(self):
        # sets the current bet of the table to 0
        self.current_bet = 0
        # deals the hole cards based on number of players in the game
        self.player_hands = [[self._game_deck.cards[cards + ((hand)*3)] for cards in range(2)] for hand in range(self.players)]
        for hand in self.player_hands:
            print(hand)
    
    def the_flop(self):
        # sets the current bet of the table to 0
        self.current_bet = 0
        # deals the flop based on number of players in the game
        self.community_cards = [self._game_deck.cards[cards + (self.players*3)] for cards in range(3)]
        # displays the flop
        self.show_the_flop()
        print(self.community_cards)
            
    def the_turn(self):
        # sets the current bet of the table to 0
        self.current_bet = 0
        # deals the turn based on number of players in the game
        self.community_cards.append(self._game_deck.cards[(self.players*3) + 3])
        # displays the turn
        self.show_the_turn()
        print(self.community_cards)

    def the_river(self):
        # sets the current bet of the table to 0
        self.current_bet = 0
        # deals the river based on number of players in the game
        self.community_cards.append(self._game_deck.cards[(self.players*3) + 4])
        # displays the river
        print(self.community_cards)
        self.show_the_river()
        
    def check_hand(self):
        # sets the hand values of every player to the lowest
        self.hand_values = [[0, 0] for hands in range(self.players)]
        # sets the hand value strings of every player to nothing
        self.hand_value_string = ['' for hands in range(self.players)]
        for player in range(self.players):
            # player's hold cards + community cards
            self.combined_hand = self.player_hands[player] + self.community_cards

            # lists of suit and value 
            combined_suit = [card.suit for card in self.combined_hand]
            combined_value = [card.value for card in self.combined_hand]
            combined_value_aces = []
            for card in self.combined_hand:
                if card.value == 14:
                    combined_value_aces.append(1)
                    combined_value_aces.append(14)
                else:
                    combined_value_aces.append(card.value)

            # counts the number of same valued cards
            value_counter = Counter(combined_value)

            # sorts the list of same valued cards by value to get the high card
            sorted_value_counter = sorted(value_counter.items(), reverse=True)

            # finds the high card
            max_value = max(sorted_value_counter, key=itemgetter(1))
            max_value_converted = self.convert_face(max_value[0])

            # removes the max value from the list and finds the second highest value
            sorted_max_value_counter = sorted_value_counter
            sorted_max_value_counter.remove(max_value)
            second_max_value = max(sorted_max_value_counter, key=itemgetter(1))
            second_max_value_converted = self.convert_face(second_max_value[0])
            sorted_max_value_counter.remove(second_max_value)
            if len(sorted_max_value_counter) > 0:
                third_max_value = max(sorted_max_value_counter, key=itemgetter(1))
                sorted_max_value_counter.remove(third_max_value)
                if len(sorted_max_value_counter) > 0:
                    fourth_max_value = max(sorted_max_value_counter, key=itemgetter(1))
                    sorted_max_value_counter.remove(fourth_max_value)
                    if len(sorted_max_value_counter) > 0:
                        fifth_max_value= max(sorted_max_value_counter, key=itemgetter(1))

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
                flush_high_list = [card.value for card in straight_flush_check]
                first_flush_high = max(flush_high_list)
                first_flush_high_converted = self.convert_face(first_flush_high)
                flush_high_list.remove(first_flush_high)
                second_flush_high = max(flush_high_list)
                flush_high_list.remove(second_flush_high)
                third_flush_high = max(flush_high_list)
                flush_high_list.remove(third_flush_high)
                fourth_flush_high = max(flush_high_list)
                flush_high_list.remove(fourth_flush_high)
                fifth_flush_high = max(flush_high_list)
            
            straight_flush_high = []
            for card in straight_flush_check:
                if card.value == 14:
                    straight_flush_high.append(1)
                    straight_flush_high.append(14)
                else:
                    straight_flush_high.append(card.value)
            straight_flush_high = self.straight_check(straight_flush_high)
            straight_flush_high_converted = self.convert_face(straight_flush_high)
        
            # checks for straights and the high card
            straight_high = self.straight_check(combined_value_aces)
            straight_high_converted = self.convert_face(straight_high)
                                             
            # checks what the hand is in descending order of values of hands
            if any(value > 4 for value in suit_counter.values()) and straight_flush_high == 'Ace':
                self.hand_value_string[player] = 'ROYAL FLUSH, ' + max_suit + ' **************************************************************************************'
                self.hand_values[player] = [9, 'A']
            elif any(value > 4 for value in suit_counter.values()) and straight_flush_high is not None:
                self.hand_value_string[player] = str(straight_flush_high_converted) + ' High Straight Flush, ' + max_suit + ' **************************************************************************************'
                self.hand_values[player] = [8, straight_flush_high]
            elif max_value_counter[4] > 0:
                self.hand_value_string[player] = 'Four of a Kind, ' + str(max_value_converted) + 's'
                if second_max_value[0] < third_max_value[0]:
                    second_max_value = third_max_value
                    self.exit_loop = 1
                self.hand_values[player] = [7, max_value[0], second_max_value[0]]
            elif max_value_counter[3] > 0 and max_value_counter[2] > 0:
                self.hand_value_string[player] = 'Full House, ' + str(max_value_converted) + 's over ' + str(second_max_value_converted) + 's'
                self.hand_values[player] = [6, max_value[0], second_max_value[0]]            
            elif any(value > 4 for value in suit_counter.values()):
                self.hand_value_string[player] =  str(first_flush_high_converted) + ' High Flush, ' + max_suit
                self.hand_values[player] = [5, first_flush_high, second_flush_high, third_flush_high, fourth_flush_high, fifth_flush_high]
            elif straight_high is not None:
                self.hand_value_string[player] = str(straight_high_converted) + ' High Straight'
                self.hand_values[player] = [4, straight_high]
            elif max_value_counter[3] > 0:
                self.hand_value_string[player] = 'Three of a Kind, ' + str(max_value_converted) + 's'
                self.hand_values[player] = [3, max_value[0], second_max_value[0], third_max_value[0]]
            elif max_value_counter[2] > 1 and second_max_value_converted != 1:
                self.hand_value_string[player] = 'Two Pair, ' + str(max_value_converted) + 's and ' + str(second_max_value_converted) + 's'
                if third_max_value[0] < fourth_max_value[0]:
                    third_max_value = fourth_max_value
                self.hand_values[player] = [2, max_value[0], second_max_value[0], third_max_value[0]]
            elif max_value_counter[2] > 0:
                self.hand_value_string[player] = 'One Pair, ' + str(max_value_converted) + 's'
                self.hand_values[player] = [1, max_value[0], second_max_value[0], third_max_value[0], fourth_max_value[0]]
            else:
                self.hand_value_string[player] = 'High Card, ' + str(max_value_converted)
                self.hand_values[player] = [0, max_value[0], second_max_value[0], third_max_value[0], fourth_max_value[0], fifth_max_value[0]]

            print('Player ' + str(player+1) + "'s hand: " + self.hand_value_string[player])

    def straight_check(self, nums):
        # checks straight with high card by making a list of consecutive ranges of values
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
            return straight_high

    def convert_face(self, card):
        if card in [14]:
            card_converted = 'Ace'
        elif card in [13]:
            card_converted = 'King'
        elif card in [12]:
            card_converted = 'Queen'
        elif card in [11]:
            card_converted = 'Jack'
        else:
            card_converted = card
        return card_converted

    def compare_hand(self):
        # sets the highest hand to -1 and winning player to -1, if -1 means no one won
        self.highest_hand = [-1]
        self.winning_player = [-1]
        self.kicker = ''
        self.kicker_value = 0
        # compares every hand value to the next, updating the winning player list if it's higher or adds to the list if they are equal
        for index, hands in enumerate(self.hand_values):
            print(hands)
            # checks if the player is in play still
            if self.in_play[index] == True:
                # checks first what kind of hand
                if hands[0] > self.highest_hand[0]:
                    self.highest_hand = hands
                    self.kicker = ''
                    self.kicker_value = 0
                    self.winning_player = [index+1]
                # checks the high card of the hand
                elif hands[0] == self.highest_hand[0]:
                    if hands[1] > self.highest_hand[1]:
                        self.highest_hand = hands
                        self.kicker = ''
                        self.kicker_value = 1
                        self.winning_player = [index+1]
                    # checks the second high card of the hand for full house and two pair
                    elif hands[1] == self.highest_hand[1]:
                        # if high card, pair, two pair, 3 of a kind, flush, full house, or four of a kind, continue to second card tiebreaker
                        if hands[0] in [0, 1, 2, 3, 5, 6, 7]:
                            if hands[2] > self.highest_hand[2]:
                                self.highest_hand = hands
                                self.kicker = self.convert_face(hands[2])
                                self.kicker_value = 2
                                if hands[0] in [2, 6]:
                                    self.kicker = ''
                                self.winning_player = [index+1]
                            # in case of ties
                            elif hands[2] == self.highest_hand[2]:
                                # if high card, pair, two pair, 3 of a kind, or flush, continue to third card tiebreaker
                                if hands[0] in [0, 1, 2, 3, 5]:
                                    if hands[3] > self.highest_hand[3]:
                                        self.highest_hand = hands
                                        self.kicker = self.convert_face(hands[3])
                                        self.kicker_value = 3
                                        self.winning_player = [index+1]
                                    elif hands[3] == self.highest_hand[3]:
                                        # if high card, pair or flush, continue to fourth card tiebreaker
                                        if hands[0] in [0, 1, 5]:
                                            if hands[4] > self.highest_hand[4]:
                                                self.highest_hand = hands
                                                self.kicker = self.convert_face(hands[4])
                                                self.kicker_value = 4
                                                self.winning_player = [index+1]
                                            elif hands[4] == self.highest_hand[4]:
                                                # if high card or flush, continue to fifth card tiebreaker
                                                if hands[0] in [0, 5]:
                                                    if hands[5] > self.highest_hand[5]:
                                                        self.highest_hand = hands
                                                        self.kicker = self.convert_face(hands[5])
                                                        self.kicker_value = 5
                                                        self.winning_player = [index+1]
                                                    # in case of ties
                                                    elif hands[5] == self.highest_hand[5]:
                                                        self.winning_player.append(index+1)
                                                    else:
                                                        if self.kicker_value <= 4:
                                                            self.kicker = self.convert_face(self.highest_hand[5])
                                                            self.kicker_value = 5
                                                # in case of ties
                                                else:
                                                    self.winning_player.append(index+1)
                                            else:
                                                if self.kicker_value <= 3:
                                                    self.kicker = self.convert_face(self.highest_hand[4])
                                                    self.kicker_value = 4
                                        # in case of ties
                                        else:
                                            self.winning_player.append(index+1)
                                    else:
                                        if self.kicker_value <= 2:
                                            self.kicker = self.convert_face(self.highest_hand[3])
                                            self.kicker_value = 3
                                # in case of ties
                                else:
                                    self.winning_player.append(index+1)
                            else:
                                if self.kicker_value <= 1:
                                    self.kicker = self.convert_face(self.highest_hand[2])
                                    self.kicker_value = 2
                                    if hands[0] in [2, 6]:
                                        self.kicker = ''
                                        self.kicker_value = 0
                        # in case of ties
                        else:
                            self.winning_player.append(index+1)
            print(self.kicker)

    def initial_graphics(self):
        self.balances_text = [None for players in range(self.players)]
        self.hole_card_1 = [None for players in range(self.players)]
        self.hole_card_2 = [None for players in range(self.players)]
        self.back_card_1 = [None for players in range(self.players)]
        self.back_card_2 = [None for players in range(self.players)]
        self.hand_text = ['' for players in range(self.players)]
        self.win = GraphWin('Poker', GetSystemMetrics(0)-100, GetSystemMetrics(1)-100)
        self.win.setBackground('dark green')

        check_rectangle = Rectangle(Point((self.win.getWidth()/2)-450, self.win.getHeight()-175), Point((self.win.getWidth()/2)-350, self.win.getHeight()-125))
        check_rectangle.setFill('dodger blue')
        check_rectangle.draw(self.win)
        check_text = Text(Point((self.win.getWidth()/2)-400, self.win.getHeight()-150), 'Check')
        check_text.setSize(20)
        check_text.draw(self.win)

        call_rectangle = Rectangle(Point((self.win.getWidth()/2)-250, self.win.getHeight()-175), Point((self.win.getWidth()/2)-150, self.win.getHeight()-125))
        call_rectangle.setFill('maroon')
        call_rectangle.draw(self.win)
        call_text = Text(Point((self.win.getWidth()/2)-200, self.win.getHeight()-150), 'Call')
        call_text.setSize(20)
        call_text.draw(self.win)
        
        raise_rectangle = Rectangle(Point((self.win.getWidth()/2)+50, self.win.getHeight()-175), Point((self.win.getWidth()/2)-50, self.win.getHeight()-125))
        raise_rectangle.setFill('purple')
        raise_rectangle.draw(self.win)
        raise_text = Text(Point((self.win.getWidth()/2), self.win.getHeight()-150), 'Raise')
        raise_text.setSize(20)
        raise_text.draw(self.win)

        fold_rectangle = Rectangle(Point((self.win.getWidth()/2)+250, self.win.getHeight()-175), Point((self.win.getWidth()/2)+150, self.win.getHeight()-125))
        fold_rectangle.setFill('red')
        fold_rectangle.draw(self.win)
        fold_text = Text(Point((self.win.getWidth()/2)+200, self.win.getHeight()-150), 'Fold')
        fold_text.setSize(20)
        fold_text.draw(self.win)

        show_cards_rectangle = Rectangle(Point((self.win.getWidth()/2)+550, self.win.getHeight()-175), Point((self.win.getWidth()/2)+350, self.win.getHeight()-125))
        show_cards_rectangle.setFill('turquoise')
        show_cards_rectangle.draw(self.win)
        show_cards_text = Text(Point((self.win.getWidth()/2)+450, self.win.getHeight()-150), 'Show Cards')
        show_cards_text.setSize(20)
        show_cards_text.draw(self.win)

        allin_rectangle = Rectangle(Point((self.win.getWidth()/2)+50, self.win.getHeight()-75), Point((self.win.getWidth()/2)-50, self.win.getHeight()-25))
        allin_rectangle.setFill('gold')
        allin_rectangle.draw(self.win)
        allin_text = Text(Point(self.win.getWidth()/2, self.win.getHeight()-50), 'All In')
        allin_text.setSize(20)
        allin_text.draw(self.win)

        self.jackpot_text = Text(Point(200, self.win.getHeight()-350), 'Current pot: $0')
        self.jackpot_text.setSize(20)
        self.jackpot_text.setTextColor('red')
        self.jackpot_text.draw(self.win)

        self.showing_cards = False

        self.current_bet_text = Text(Point(200, self.win.getHeight()-400), 'Current bet: $0')
        self.current_bet_text.setSize(20)
        self.current_bet_text.setTextColor('red')
        self.current_bet_text.draw(self.win)

        self.player_action_text = Text(Point(1000, self.win.getHeight()-350), '')
        self.player_action_text.setSize(20)
        self.player_action_text.setTextColor('red')
        self.player_action_text.draw(self.win)

        for players in range(self.players):
            self.balances_text[players] = Text(Point((self.win.getWidth()/(self.players+1)*(players+1)), self.win.getHeight()-250), 'Player ' + str(players+1) + ' Balance: $' + str(self.wallet[players]))
            self.balances_text[players].setTextColor('red')
            self.balances_text[players].setSize(20)
            self.balances_text[players].draw(self.win)

    def show_hole_cards(self, player):
        self.showing_cards = True
        self.hole_card_1[player] = Image(Point((self.win.getWidth()/(self.players+1)*(player+1))-25, 150), self.player_hands[player][0].image_file)
        self.hole_card_1[player].draw(self.win)
        self.hole_card_2[player] = Image(Point((self.win.getWidth()/(self.players+1)*(player+1))+25, 150), self.player_hands[player][1].image_file)
        self.hole_card_2[player].draw(self.win)

    def hide_hole_cards(self, player):
        self.showing_cards = False
        self.hole_card_1[player].undraw()
        self.hole_card_2[player].undraw()

    def show_back_cards(self, player):
        self.back_card_1[player] = Image(Point((self.win.getWidth()/(self.players+1)*(player+1))-25, 150), 'backCard.ppm')
        self.back_card_1[player].draw(self.win)
        self.back_card_2[player] = Image(Point((self.win.getWidth()/(self.players+1)*(player+1))+25, 150), 'backCard.ppm')
        self.back_card_2[player].draw(self.win)

    def hide_back_cards(self, player):
        self.back_card_1[player].undraw()
        self.back_card_2[player].undraw()

    def show_the_flop(self):
        self.community_card_1 = Image(Point(self.win.getWidth()/2-100, self.win.getHeight()/2), self.community_cards[0].image_file)
        self.community_card_2 = Image(Point((self.win.getWidth()/2)-50, self.win.getHeight()/2), self.community_cards[1].image_file)
        self.community_card_3 = Image(Point((self.win.getWidth()/2), self.win.getHeight()/2), self.community_cards[2].image_file)
        self.community_card_1.draw(self.win)
        self.community_card_2.draw(self.win)
        self.community_card_3.draw(self.win)

    def show_the_turn(self):
        self.community_card_4 = Image(Point((self.win.getWidth()/2)+50, self.win.getHeight()/2), self.community_cards[3].image_file)
        self.community_card_4.draw(self.win)
        
    def show_the_river(self):
        self.community_card_5 = Image(Point((self.win.getWidth()/2)+100, self.win.getHeight()/2), self.community_cards[4].image_file)
        self.community_card_5.draw(self.win)

    def hide_community_cards(self):
        self.community_card_1.undraw()
        self.community_card_2.undraw()
        self.community_card_3.undraw()
        self.community_card_4.undraw()
        self.community_card_5.undraw()

    def show_hand_text(self, player):
        self.hand_text[player] = Text(Point((self.win.getWidth()/(self.players+1)*(player+1)), 30), self.hand_value_string[player])
        for players in self.winning_player:
            if (players-1) == player:
                if self.kicker != '':
                    self.hand_text[player] = Text(Point((self.win.getWidth()/(self.players+1)*(player+1)), 30), self.hand_value_string[player] + ' with ' + str(self.kicker) + ' kicker')
                self.hand_text[player].setTextColor('red')
        self.hand_text[player].draw(self.win)

    def hide_hand_text(self, player):
        self.hand_text[player].undraw()

    def update_balances_text(self):
        for players in range(self.players):
            self.balances_text[players].undraw()
            self.balances_text[players] = Text(Point((self.win.getWidth()/(self.players+1)*(players+1)), self.win.getHeight()-250), 'Player ' + str(players+1) + ' Balance: $' + str(self.wallet[players]))
            self.balances_text[players].setTextColor('red')
            self.balances_text[players].setSize(20)
            self.balances_text[players].draw(self.win)

    def update_current_bet_text(self):
        self.current_bet_text.undraw()
        self.current_bet_text = Text(Point(200, self.win.getHeight()/2), 'Current bet: $' + str(self.current_bet))
        self.current_bet_text.setSize(20)
        self.current_bet_text.setTextColor('red')
        self.current_bet_text.draw(self.win)

    def update_jackpot_text(self):
        self.jackpot_text.undraw()
        self.jackpot_text = Text(Point(200, (self.win.getHeight()/2)-50), 'Current pot: $' + str(self.jackpot))
        self.jackpot_text.setSize(20)
        self.jackpot_text.setTextColor('red')
        self.jackpot_text.draw(self.win)

    def update_player_action_text(self, action):
        self.player_action_text.undraw()
        self.player_action_text = Text(Point(self.win.getWidth()-300, self.win.getHeight()/2), action)
        self.player_action_text.setSize(20)
        self.player_action_text.setTextColor('red')
        self.player_action_text.draw(self.win)

    def get_input(self):
        decision = ''
        input = self.win.getMouse()
        if input.getY() >= (self.win.getHeight()-175) and input.getY() <= (self.win.getHeight()-125):
            if input.getX() >= ((self.win.getWidth()/2)-450) and input.getX() <= ((self.win.getWidth()/2)-350):
                decision = 'check'
            elif input.getX() >= ((self.win.getWidth()/2)-250) and input.getX() <= ((self.win.getWidth()/2)-150):
                decision = 'call'
            elif input.getX() >= ((self.win.getWidth()/2)-50) and input.getX() <= ((self.win.getWidth()/2)+50):
                decision = 'raise'
            elif input.getX() >= ((self.win.getWidth()/2)+150) and input.getX() <= ((self.win.getWidth()/2)+250):
                decision = 'fold'
            elif input.getX() >= ((self.win.getWidth()/2)+350) and input.getX() <= ((self.win.getWidth()/2)+550):
                decision = 'show cards'
        elif input.getY() >= (self.win.getHeight()-75) and input.getY() <= (self.win.getHeight()-25):
            if input.getX() >= ((self.win.getWidth()/2)-50) and input.getX() <= ((self.win.getWidth()/2)+50):
                decision = 'all in'
        return decision

    def get_keyboard(self):
        amount = ''
        current_key = ''
        while current_key != 'Return':
            current_key = self.win.getKey()        
            if current_key == 'BackSpace':
                string_list = list(amount)
                print(string_list)
                del(string_list[len(string_list)-1])
                print(string_list)
                amount = ''.join(string_list)
                self.update_player_action_text('Bet amount?: $' + amount)
            elif current_key != 'Return':
                amount += current_key
                self.update_player_action_text('Bet amount?: $' + amount)
        if amount == '':
            amount = '0'
        return amount

    def end_game(self):
        winning_player = 0
        for players, money in enumerate(self.wallet):
            if money > self.wallet[winning_player]:
                winning_player = players
        self.player_action_text = Text(Point(self.win.getWidth()/2, self.win.getHeight()/2), 'Player ' + str(winning_player+1) + ' wins it all' )
        self.player_action_text.setSize(36)
        self.player_action_text.setTextColor('blue')
        self.player_action_text.draw(self.win)
        self.win.getMouse()
        self.win.close()

while True:
    game = Poker()
    game.start_game(2)
    print(game.combined_hand)