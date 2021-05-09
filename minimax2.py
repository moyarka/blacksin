import random
from copy import deepcopy
from operator import itemgetter
MAXIMIZER, MINIMIZER = (0, 1)

class Player:
    def __init__(self, name, num_of_cards):
        """
        The base player class of the game
        Inputs
        -----------
        name = (str) player's name
        num_of_cards = (int) number of cards in the deck
        """
        self.name = name
        self.deck_count = num_of_cards
        self.target = self.deck_count * 2 - 1
        self.cards = []
        self.erases_remaining = self.deck_count // 5
        self.has_stopped = False

    def make_copy(self):
        res = Player(self.name, self.deck_count)
        res.cards = list(self.cards)
        res.erases_remaining = self.erases_remaining
        res.has_stopped = self.has_stopped
        return res
    
    def draw_card(self, card):
        """
        draws a card, and adds it to player cards
        Input
        -------------
        card: (int) the card to be added
        """
        self.cards.append(card)

    def print_info(self):
        """
        prints info of the player
        """
        # print(f"{self.name}'s cards: ", end='')
        # for c in self.cards:
            # print(f'{c}, ', end='')
        # print(f'sum: {sum(self.cards)}')
    
    def get_margin(self):
        """
        returns the margin left to target by the player
        Output
        ----------
        (int) margin to target
        """
        return self.target - sum(self.cards)
    
    def cpu_play(self, seen_cards, deck, enemies_cards):
        """
        The function for cpu to play the game
        Inputs
        ----------
        seen_cards:     (list of ints) the cards that have been seen until now
        deck:           (list of ints) the remaining playing deck of the game
        enemies_cards:  (list of ints) the cards that the enemy currently has.
        Output
        ----------
        (str) a command given to the game
        
        """
        if (len(deck) > 0):
            next_card_in_deck = deck[0]
        else:
            next_card_in_deck = 0
        if (len(deck) > 1):
            next_enemy_card_in_deck = deck[1]
        else:
            next_enemy_card_in_deck = 0
        amount_to_target = self.target - sum(self.cards)
        amount_with_next_card = self.target - (sum(self.cards) + next_card_in_deck)
        enemies_amount_to_target = self.target - sum(enemies_cards)
        enemies_amount_with_next_card = self.target - (sum(enemies_cards) + next_enemy_card_in_deck)
        _stop_condition = amount_to_target < next_card_in_deck and self.erases_remaining <= 0
        _draw_condition_1 = next_card_in_deck != 0
        _draw_condition_2 = amount_with_next_card >= 0
        _erase_condition = self.erases_remaining > 0
        _erase_self_condition = amount_to_target < 0
        _erase_opponent_condition_or = enemies_amount_to_target < (self.target // 7)
        _erase_opponent_condition_or_2 = enemies_amount_with_next_card < (self.target // 7) 
        _erase_opponent_condition_or_3 = enemies_amount_with_next_card <= amount_with_next_card
        _erase_opponent_condition_or_4 = enemies_amount_to_target <= amount_to_target
        _erase_opponent_condition = _erase_opponent_condition_or or _erase_opponent_condition_or_2 or _erase_opponent_condition_or_3
        _erase_opponent_condition = _erase_opponent_condition or _erase_opponent_condition_or_4 
        if (_stop_condition):
            return 'stop'
        elif (_draw_condition_1 and _draw_condition_2):
            return 'draw'
        elif(_erase_self_condition and _erase_condition):
            return 'erase_self'
        elif(_erase_opponent_condition and _erase_condition):
            return 'erase_opponent'
        else:
            return 'stop'
    
    def erase(self, target):
        """
        erases the last card of the target
        Input
        ---------
        target: (Player obj) the player whos last card is about to be erased
        """
        if (len(target.cards) == 0):
            # print(f'{target.name} has no more eraseble cards!')
            return
        if (self.erases_remaining > 0):
            self.erases_remaining -= 1
            card = target.cards.pop(-1)
            # print(f'{self.name} erased {card} from {target.name}\'s deck!')
            return
        # print(f'{self.name} has no more erases remaining!')

    def get_player_cards(self):
        return self.cards

    def get_erases_remained(self):
        return self.erases_remaining

class Blacksin:
    def __init__(self, deck_count=21):
        """
        The main game class
        Inputs
        -----------
        deck_count = (int) number of cards in the deck
        """
        self.deck_count = deck_count
        self.target = self.deck_count * 2 - 1
        self.player = Player('player', deck_count)
        self.opponent = Player('opponent', deck_count)
        self.deck = self.shuffle_cards()
        self.seen_cards = []
        
        self.best_move = {}

    def make_copy(self):
        res = Blacksin(self.deck_count)
        res.deck = list(self.deck)
        res.player = self.player.make_copy()
        res.opponent = self.opponent.make_copy()
        res.seen_cards = self.seen_cards
        
        return res
        
    def get_state(self):
        res = []
        res.append(tuple(self.player.cards))
        res.append(tuple(self.opponent.cards))
        res.append(len(self.deck))
        res.append((self.player.erases_remaining, self.opponent.erases_remaining))
        res.append((self.player.has_stopped, self.opponent.has_stopped))
        
        return tuple(res)
    
    def shuffle_cards(self):
        """ 
        shuffles cards for deck creation
        """
        return list(random.sample(range(1, self.deck_count + 1), self.deck_count))

    def draw_card(self):
        """ 
        draws a card from deck, if non is remaining, ends the game.
        """
        if (len(self.deck) > 0):
            card = self.deck.pop(0)
            self.seen_cards.append(card)
            return card
        # print('The deck is empty! ending game...')
        self.opponent.has_stopped = True
        self.player.has_stopped = True
        return -1

    def handout_cards(self):
        """ 
        hands out cards to players
        """
        self.player.draw_card(self.draw_card())
        self.opponent.draw_card(self.draw_card())
        self.player.draw_card(self.draw_card())
        self.opponent.draw_card(self.draw_card())
    
    def handle_input(self, _input, player):
        """ 
        handles input
        Input
        ------------
        _input: (str) input given by the player
        player: (Player obj)the player that is giving the input
        
        """
        if (player is self.player):
            opponent = self.opponent
        else:
            opponent = self.player
        if (_input == 'stop' or _input == 's'):
            player.has_stopped = True
            # print(f'{player.name} has stopped')
        elif (_input == 'draw' or _input == 'd'):
            card = self.draw_card()
            if (card == -1): return True
            player.draw_card(card)
            # print(f'{player.name} drawed a card: {card}')
        elif ((_input == 'erase_self' or _input == 'es')):
            player.erase(player)
        elif ((_input == 'erase_opponent' or _input == 'eo')):
            player.erase(opponent)
        else:
            # print('ERROR: unknown command')
            return False
        return True

    def maximizer(self, depth):
        # print(f'\nMAXIMIZER: depth: {depth}, current_state is: {self.get_state()}\n')

        if self.player.has_stopped:
            stopped_copy = self.make_copy()
            val = stopped_copy.minimax(MINIMIZER, depth + 1)
            return [val[0], '\0']
        
        scores = []
        
        # Draw a Card
        if len(self.deck) > 0:
            draw_copy = self.make_copy()
            draw_copy.handle_input('d', draw_copy.player)
            draw_val = draw_copy.minimax(MINIMIZER, depth + 1)
            scores.append([draw_val[0], 'd'])

        # Stop
        if not self.player.has_stopped:
            stopping_copy = self.make_copy()
            stopping_copy.handle_input('s', stopping_copy.player)
            stop_val = stopping_copy.minimax(MINIMIZER, depth + 1)
            scores.append([stop_val[0], 's'])
        
        # Player Erases Card from Himself
        if self.player.erases_remaining > 0 and len(self.player.cards) > 0:
            erase_self_copy = self.make_copy()
            erase_self_copy.handle_input('es', erase_self_copy.player)
            erase_self_val = erase_self_copy.minimax(MINIMIZER, depth + 1)
            scores.append([erase_self_val[0], 'es'])
    
        if self.player.erases_remaining > 0 and len(self.opponent.cards) > 0:
            erase_opponent_copy = self.make_copy()
            erase_opponent_copy.handle_input('eo', erase_opponent_copy.player)
            eo_val = erase_opponent_copy.minimax(MINIMIZER, depth + 1)
            scores.append([eo_val[0], 'eo'])
    
        sorted_scores = sorted(scores, key=itemgetter(0), reverse=True)
        return sorted_scores[0]
    
    def minimizer(self, depth):
        # print(f'\nMINIMIZER: depth: {depth}, current_state is: {self.get_state()}\n')
        if self.opponent.has_stopped:
            stopped_copy = self.make_copy()
            val = stopped_copy.minimax(MAXIMIZER, depth + 1)
            return [val[0], '\0']
        
        scores = []
        
        if len(self.deck) > 0:
            draw_copy = self.make_copy()
            draw_copy.handle_input('d', draw_copy.opponent)
            draw_val = draw_copy.minimax(MAXIMIZER, depth + 1)
            scores.append([draw_val[0], 'd'])

        if not self.opponent.has_stopped:
            stopping_copy = self.make_copy()
            stopping_copy.handle_input('s', stopping_copy.opponent)
            stop_val = stopping_copy.minimax(MAXIMIZER, depth + 1)
            scores.append([stop_val[0], 's'])

        if self.opponent.erases_remaining > 0 and len(self.opponent.cards) > 0:
            erase_self_copy = self.make_copy()
            erase_self_copy.handle_input('es', erase_self_copy.opponent)
            es_val = erase_self_copy.minimax(MAXIMIZER, depth + 1)
            scores.append([es_val[0], 'es'])

        if self.opponent.erases_remaining > 0 and len(self.player.cards) > 0:
                erase_opponent_copy = self.make_copy()
                erase_opponent_copy.handle_input('eo', erase_opponent_copy.opponent)
                eo_val = erase_opponent_copy.minimax(MAXIMIZER, depth + 1)
                scores.append([eo_val[0], 'eo'])

        sorted_scores = sorted(scores, key=itemgetter(0), reverse=False)
        return sorted_scores[0]
    
    def minimax(self, mm_turn, depth):
        if (self.player.has_stopped and self.opponent.has_stopped):
            return [self.check_for_winners(), '\0']
        
        if depth > 4:
            return [self.check_for_winners(), '\0']
        
        if mm_turn == MAXIMIZER:
            return self.maximizer(depth)
        if mm_turn == MINIMIZER:
            return self.minimizer(depth)
    
    def get_player_input(self):
        # """TODO"""
        # print("complete me!")
        # your_input = 'some input'
        your_input = self.minimax(MAXIMIZER, 0)[1]
        self.handle_input(your_input, self.player)
            
    def opponent_play(self):
        """
        function for opponent to play it's turn
        """
        try:
            opponent_input = self.opponent.cpu_play(self.seen_cards, self.deck, self.player.cards)
        except:
            opponent_input = 'stop'
        self.handle_input(opponent_input, self.opponent)

    def check_for_winners(self):
        """
        checks for winners.
        Output
        -----------
        (int) returns 1 if player wins, 0 if draw and -1 if opponent wins
        """
        # self.opponent.print_info()
        # self.player.print_info()
        player_margin = self.player.get_margin()
        opponent_margin = self.opponent.get_margin()
        player_win_condition_1 = opponent_margin < 0 and player_margin >= 0
        player_win_condition_2 = opponent_margin >=0 and player_margin >= 0 and player_margin < opponent_margin
        draw_condition_1 = opponent_margin < 0 and player_margin < 0
        draw_condition_2 = opponent_margin >= 0 and player_margin >= 0 and player_margin == opponent_margin
        opponent_win_condition_1 = player_margin < 0 and opponent_margin >= 0
        opponent_win_condition_2 = opponent_margin >=0 and player_margin >= 0 and player_margin > opponent_margin
        if (player_win_condition_1 or player_win_condition_2):
            # print(f'the winner is the {self.player.name}!')
            return 1
        elif(draw_condition_1 or draw_condition_2):
            # print('the game ends in a draw!')
            return 0
        elif(opponent_win_condition_1 or opponent_win_condition_2):
            # print(f'the winner is the {self.opponent.name}!')
            return -1
        else:
            print('an error has accurred! exiting...')
            exit()

    def print_deck(self):
        """
        prints the current deck of the game
        """
        # print('full deck: [top] ', end='')
        # for i in self.deck:
            # print(i, end=' ')
        # print('[bottom]')

    def run(self):
        """
        main function to run the game with
        """
        # print('\nstarting game... shuffling... handing out cards...')
        # print(f'remember, you are aiming for nearest to: {self.target}')
        # self.print_deck()
        self.handout_cards()
        turn = 0
        while(not self.player.has_stopped or not self.opponent.has_stopped):
            if (turn == 0):
                if (not self.player.has_stopped):
                    # self.opponent.print_info()
                    # self.player.print_info()
                    self.get_player_input()
                    # print()
            else:
                if (not self.opponent.has_stopped):
                    # print('opponent playing...')
                    self.opponent_play()
                    # print()
            turn = 1 - turn
        # print('\nand the winner is...')
        return self.check_for_winners()

# Example of using the game class
res = []
for i in range(100):
    print(f'running test {i + 1}', end=', ')
    game = Blacksin(deck_count=21)
    res.append(game.run())
    print(f'result is: {res[-1]}')

print()
print(f'performance: {res.count(1)/len(res) * 100}%')