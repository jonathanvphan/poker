from card import Deck
from collections import Counter
from operator import itemgetter
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
        self.initial_graphics()
        self.check_balances()
        while self.players_with_cash:
            self._game_deck.shuffle()
            self.play_round()
            self.check_balances()
    
    def play_round(self):
        self.in_play = [True for check in range(self.players)]
        self.hole_card_1 = [None for players in range(self.players)]
        self.hole_card_2 = [None for players in range(self.players)]
        self.hand_text = ['' for players in range(self.players)]
        self.jackpot = 0
        self.update_jackpot_text()
        self.hole_cards()
        self.check_players()
        self.turn_decision()
        self.update_jackpot_text()
        self.update_balances_text()
        print('Current pot: $' + str(self.jackpot))
        self.the_flop()
        self.check_players()
        self.turn_decision() 
        self.update_jackpot_text()
        self.update_balances_text()
        print('Current pot: $' + str(self.jackpot))
        self.the_turn()
        self.check_players()
        self.turn_decision() 
        self.update_jackpot_text()
        self.update_balances_text()
        print('Current pot: $' + str(self.jackpot))
        self.the_river()
        self.check_players()
        self.turn_decision()
        self.update_jackpot_text()
        self.update_balances_text()
        print('current pot: $' + str(self.jackpot))
        self.check_hand()
        self.compare_hand()
        if self.winning_player[0] != -1:
            if len(self.winning_player) > 1:
                winning_player_string = ', '.join([str(player) for player in self.winning_player])
                print('Winning Hand: Players ' + winning_player_string)
                for payout in self.winning_player:
                    self.wallet[payout-1] += self.jackpot/len(self.winning_player)
            else:
                print('Winning Hand: Player ' + str(self.winning_player[0]))
                self.wallet[self.winning_player[0]-1] += self.jackpot
        else:
            print('No player left in play')
        for players in range(self.players):
            self.show_hole_cards(players)
            self.show_hand_text(players)
        self.win.getMouse()
        for players in range(self.players):
            self.hide_hole_cards(players)
            self.hide_hand_text(players)
        self.hide_community_cards()
        self.update_balances_text()
    
    def give_money(self):
        self.wallet = []
        for money in range(self.players):
            self.wallet.append(500)

    def check_balances(self):
        balances = [money for money in self.wallet]
        max_balance = max(balances)
        balances.remove(max_balance)
        print(balances)
        overall_balances = [True for players in balances if players > 0]
        self.players_with_cash = any(overall_balances)

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
                    print('Player ' + str(player_turn+1) + ': $' + str(self.wallet[player_turn]))
                    self.show_hole_cards(player_turn)
                    #decision = input('Player ' + str(player_turn+1) + ': check, call, raise, or fold? ')
                    decision = self.get_input()
                    if decision == 'check':
                        if self.players_current_bet[player_turn-1] == self.players_current_bet[player_turn]:
                            self.check(player_turn)
                            bet_raised[player_turn] = True
                            valid = True
                        else:
                            print('Cannot check with current bet of $' + str(self.current_bet))
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
                                print('You cannot call your own bet of $' + str(self.current_bet))
                        else:
                            print('Insufficent funds')
                    elif decision == 'raise':
                        amount = int(input('Bet amount?: $'))
                        if amount < self.wallet[player_turn]:
                            if amount > self.current_bet:
                                self.raise_bet(player_turn, amount)
                                bet_raised = [False for bets in range(self.players)]
                                bet_raiser = player_turn
                                valid = True
                            else:
                                print('Raise must be greater than current bet of $' + str(self.current_bet))
                        else:
                            print('Insufficient funds')
                    elif decision == 'fold':
                        self.fold(player_turn)
                        bet_raised[player_turn] = True
                        self.players_current_bet[player_turn] = self.current_bet
                        valid = True
                    self.hide_hole_cards(player_turn)


    def check_players(self):
        self.players_current_bet = [0 for players in range(self.players)]

    def check(self, player):
        print('Player ' + str(player+1) + ' checked')

    def raise_bet(self, player, amount):
        print('Player ' + str(player+1) + ' raised bet from $' + str(self.current_bet) + ' to $' + str(amount))
        self.players_current_bet[player] = amount
        self.wallet[player] -= amount
        self.current_bet = amount
        self.jackpot += amount

    def call_bet(self, player):
        print('Player ' + str(player+1) + ' called bet of $' + str(self.current_bet))
        self.wallet[player] += self.players_current_bet[player]
        self.players_current_bet[player] = self.current_bet
        self.wallet[player] -= self.current_bet
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
        self.show_the_flop()
        print(self.community_cards)
            
    def the_turn(self):
        self.current_bet = 0
        self.community_cards.append(self._game_deck.cards[(self.players*3) + 3])
        self.show_the_turn()
        print(self.community_cards)

    def the_river(self):
        self.current_bet = 0
        self.community_cards.append(self._game_deck.cards[(self.players*3) + 4])
        print(self.community_cards)
        self.show_the_river()
        
    def check_hand(self):
        self.hand_values = [(0, 0) for hands in range(self.players)]
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
                flush_high = [card.value for card in straight_flush_check]
                flush_high = max(flush_high)
                if flush_high in [14]:
                    flush_high_converted = 'Ace'
                elif flush_high in [13]:
                    flush_high_converted = 'King'
                elif flush_high in [12]:
                    flush_high_converted = 'Queen'
                elif flush_high in [11]:
                    flush_high_converted = 'Jack'
                else:
                    flush_high_converted = flush_high
            
            straight_flush_high = []
            for card in straight_flush_check:
                if card.value == 14:
                    straight_flush_high.append(1)
                    straight_flush_high.append(14)
                else:
                    straight_flush_high.append(card.value)
            straight_flush_high = self.straight_check(straight_flush_high)
        
            # checks for straights and the high card
            straight_high = self.straight_check(combined_value_aces)

            # converts face card value to name
            if max_value[0] in [14]:
                max_value_converted = 'Ace'
            elif max_value[0] in [13]:
                max_value_converted = 'King'
            elif max_value[0] in [12]:
                max_value_converted = 'Queen'
            elif max_value[0] in [11]:
                max_value_converted = 'Jack'
            else:
                max_value_converted = max_value[0]
            if second_max_value[0] in [14]:
                second_max_value_converted = 'Ace'
            elif second_max_value[0] in [13]:
                second_max_value_converted = 'King'
            elif second_max_value[0] in [12]:
                second_max_value_converted = 'Queen'
            elif second_max_value[0] in [11]:
                second_max_value_converted = 'Jack'
            else:
                second_max_value_converted = second_max_value[0]
            if straight_high in [14]:
                straight_high_converted = 'Ace'
            elif straight_high in [13]:
                straight_high_converted = 'King'
            elif straight_high in [12]:
                straight_high_converted = 'Queen'
            elif straight_high in [11]:
                straight_high_converted = 'Jack'
            else:
                straight_high_converted = straight_high
            if straight_flush_high in [14]:
                straight_flush_high_converted = 'Ace'
            elif straight_flush_high in [13]:
                straight_flush_high_converted = 'King'
            elif straight_flush_high in [12]:
                straight_flush_high_converted = 'Queen'
            elif straight_flush_high in [11]:
                straight_flush_high_converted = 'Jack'
            else:
                straight_flush_high_converted = straight_flush_high
                    
            # checks what the hand is in descending order of values of hands
            if any(value > 4 for value in suit_counter.values()) and straight_flush_high == 'Ace':
                self.hand_value_string[player] = 'ROYAL FLUSH, ' + max_suit + ' **************************************************************************************'
                self.hand_values[player] = [9, 'A']
            elif any(value > 4 for value in suit_counter.values()) and straight_flush_high is not None:
                self.hand_value_string[player] = str(straight_flush_high_converted) + ' High Straight Flush, ' + max_suit + ' **************************************************************************************'
                self.hand_values[player] = [8, straight_flush_high]
            elif max_value_counter[max_value_counter[4] > 0] > 0:
                self.hand_value_string[player] = 'Four of a Kind, ' + str(max_value_converted) + 's'
                self.hand_values[player] = [7, max_value[0]]
            elif max_value_counter[3] > 0 and max_value_counter[2] > 0:
                self.hand_value_string[player] = 'Full House, ' + str(max_value_converted) + 's over ' + str(second_max_value_converted) + 's'
                self.hand_values[player] = [6, max_value[0], second_max_value[0]]            
            elif any(value > 4 for value in suit_counter.values()):
                self.hand_value_string[player] =  str(flush_high_converted) + ' High Flush, ' + max_suit
                self.hand_values[player] = [5, flush_high]
            elif straight_high is not None:
                self.hand_value_string[player] = str(straight_high_converted) + ' High Straight'
                self.hand_values[player] = [4, straight_high]
            elif max_value_counter[3] > 0:
                self.hand_value_string[player] = 'Three of a Kind, ' + str(max_value_converted) + 's'
                self.hand_values[player] = [3, max_value[0]]
            elif max_value_counter[2] > 1 and second_max_value_converted != 1:
                self.hand_value_string[player] = 'Two Pair, ' + str(max_value_converted) + 's and ' + str(second_max_value_converted) + 's'
                self.hand_values[player] = [2, max_value[0], second_max_value[0]]
            elif max_value_counter[2] > 0:
                self.hand_value_string[player] = 'One Pair, ' + str(max_value_converted) + 's'
                self.hand_values[player] = [1, max_value[0]]
            else:
                self.hand_value_string[player] = 'High Card, ' + str(max_value_converted)
                self.hand_values[player] = [0, max_value[0]]

            print('Player ' + str(player+1) + "'s hand: " + self.hand_value_string[player])

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
            return straight_high

    def compare_hand(self):
        self.highest_hand = [-1]
        self.winning_player = [-1]
        for index, hands in enumerate(self.hand_values):
            if self.in_play[index] == True:
                if hands[0] > self.highest_hand[0]:
                    self.highest_hand = hands
                    self.winning_player = [index+1]
                elif hands[0] == self.highest_hand[0]:
                    if hands[1] > self.highest_hand[1]:
                        self.highest_hand = hands
                        self.winning_player = [index+1]
                    elif hands[1] == self.highest_hand[1]:
                        if hands[0] == 6 or hands[0] == 2:
                            if hands[2] > self.highest_hand[2]:
                                self.highest_hand = hands
                                self.winning_player = [index+1]
                            elif hands[2] == self.highest_hand[2]:
                                self.winning_player.append(index+1)
                        else:
                            self.winning_player.append(index+1)

    def initial_graphics(self):
        self.balances_text = [None for players in range(self.players)]
        self.win = GraphWin('Poker', 1400, 700)
        self.win.yUp()
        self.win.setBackground('green')

        check_rectangle = Rectangle(Point(350, 175), Point(250, 125))
        check_rectangle.setFill('blue')
        check_rectangle.draw(self.win)
        check_text = Text(Point(300, 150), 'Check')
        check_text.setSize(20)
        check_text.draw(self.win)

        call_rectangle = Rectangle(Point(550, 175), Point(450, 125))
        call_rectangle.setFill('yellow')
        call_rectangle.draw(self.win)
        call_text = Text(Point(500, 150), 'Call')
        call_text.setSize(20)
        call_text.draw(self.win)
        
        raise_rectangle = Rectangle(Point(750, 175), Point(650, 125))
        raise_rectangle.setFill('purple')
        raise_rectangle.draw(self.win)
        raise_text = Text(Point(700, 150), 'Raise')
        raise_text.setSize(20)
        raise_text.draw(self.win)

        fold_rectangle = Rectangle(Point(950, 175), Point(850, 125))
        fold_rectangle.setFill('red')
        fold_rectangle.draw(self.win)
        fold_text = Text(Point(900, 150), 'Fold')
        fold_text.setSize(20)
        fold_text.draw(self.win)

        self.jackpot_text = Text(Point(200, 350), 'Current pot: $0')
        self.jackpot_text.setSize(20)
        self.jackpot_text.setTextColor('red')
        self.jackpot_text.draw(self.win)

        for players in range(self.players):
            self.balances_text[players] = Text(Point(((self.win.getWidth()/self.players)/self.players)*((players+(1/self.players))*self.players), 100), 'Player ' + str(players+1) + ' Balance: $' + str(self.wallet[players]))
            self.balances_text[players].setTextColor('red')
            self.balances_text[players].setSize(20)
            self.balances_text[players].draw(self.win)

    def show_hole_cards(self, player):
        self.hole_card_1[player] = Image(Point(((self.win.getWidth()/self.players)/self.players)*((player+(1/self.players))*self.players)-50, self.win.getHeight()-150), self.player_hands[player][0].image_file)
        self.hole_card_1[player].draw(self.win)
        self.hole_card_2[player] = Image(Point(((self.win.getWidth()/self.players)/self.players)*((player+(1/self.players))*self.players), self.win.getHeight()-150), self.player_hands[player][1].image_file)
        self.hole_card_2[player].draw(self.win)

    def hide_hole_cards(self, player):
        self.hole_card_1[player].undraw()
        self.hole_card_2[player].undraw()

    def show_the_flop(self):
        self.community_card_1 = Image(Point(550, 300), self.community_cards[0].image_file)
        self.community_card_2 = Image(Point(600, 300), self.community_cards[1].image_file)
        self.community_card_3 = Image(Point(650, 300), self.community_cards[2].image_file)
        self.community_card_1.draw(self.win)
        self.community_card_2.draw(self.win)
        self.community_card_3.draw(self.win)

    def show_the_turn(self):
        self.community_card_4 = Image(Point(700, 300), self.community_cards[3].image_file)
        self.community_card_4.draw(self.win)
        
    def show_the_river(self):
        self.community_card_5 = Image(Point(750, 300), self.community_cards[4].image_file)
        self.community_card_5.draw(self.win)

    def hide_community_cards(self):
        self.community_card_1.undraw()
        self.community_card_2.undraw()
        self.community_card_3.undraw()
        self.community_card_4.undraw()
        self.community_card_5.undraw()

    def show_hand_text(self, player):
        self.hand_text[player] = Text(Point(((self.win.getWidth()/self.players)/self.players)*((player+(1/self.players))*self.players)-50, self.win.getHeight()-30), self.hand_value_string[player])
        for players in self.winning_player:
            if (players-1) == player:
                self.hand_text[player].setTextColor('red')
        self.hand_text[player].draw(self.win)

    def hide_hand_text(self, player):
        self.hand_text[player].undraw()

    def update_balances_text(self):
        for players in range(self.players):
            self.balances_text[players].undraw()
            self.balances_text[players] = Text(Point(((self.win.getWidth()/self.players)/self.players)*((players+(1/self.players))*self.players), 100), 'Player ' + str(players+1) + ' Balance: $' + str(self.wallet[players]))
            self.balances_text[players].setTextColor('red')
            self.balances_text[players].setSize(20)
            self.balances_text[players].draw(self.win)

    def update_jackpot_text(self):
        self.jackpot_text.undraw()
        self.jackpot_text = Text(Point(200, 350), 'Current pot: $' + str(self.jackpot))
        self.jackpot_text.setSize(20)
        self.jackpot_text.setTextColor('red')
        self.jackpot_text.draw(self.win)

    def get_input(self):
        decision = ''
        input = self.win.getMouse()
        if input.getY() >= 125 and input.getY() <= 175:
            if input.getX() >= 250 and input.getX() <= 350:
                decision = 'check'
            elif input.getX() >= 450 and input.getX() <= 550:
                decision = 'call'
            elif input.getX() >= 650 and input.getX() <= 750:
                decision = 'raise'
            elif input.getX() >= 850 and input.getX() <= 950:
                decision = 'fold'
        return decision

count = 0
while True:
    game = Poker()
    game.start_game(3)
    print(game.combined_hand)
    count += 1
    print(count)