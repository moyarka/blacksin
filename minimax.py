import random
from operator import itemgetter
MAXIMIZER, MINIMIZER = (0, 1)
MINIMAX, ALPHABETA = (0, 1)
from termcolor import colored

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
        res.cards = self.cards[:]
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
    def __init__(self, deck_count=21, evaluator=ALPHABETA):
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
        
        self.evaluator = evaluator

    def make_copy(self):
        res = Blacksin(self.deck_count)
        res.player = self.player.make_copy()
        res.opppnent = self.opponent.make_copy()
        res.deck = self.deck[:]
        res.seen_cards = self.seen_cards[:]
    
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
            print('ERROR: unknown command')
            return False
        return True

    def maximizer(self, depth):
        # print(f'\nMAXIMIZER: depth: {depth}, current_state is: {self.get_state()}\n')    
        if self.player.has_stopped:
            val = self.minimax(MINIMIZER, depth + 1)
            return [val[0], 's']
        
        scores = []
        
        if len(self.deck) > 0:
            self.handle_input('d', self.player)
            
            draw_val = self.minimax(MINIMIZER, depth + 1)
            
            self.deck.insert(0, self.player.cards.pop())
            self.seen_cards.pop()
            scores.append([draw_val[0], 'd'])

        if not self.player.has_stopped:
            self.handle_input('s', self.player)
            
            stop_val = self.minimax(MINIMIZER, depth + 1)
            
            self.player.has_stopped = False
            scores.append([stop_val[0], 's'])
                
        if self.player.erases_remaining > 0 and len(self.player.cards) > 0:
            last_card = self.player.cards[-1]
            self.handle_input('es', self.player)
            
            es_val = self.minimax(MINIMIZER, depth + 1)
            
            self.player.cards.append(last_card)
            self.player.erases_remaining += 1
            scores.append([es_val[0], 'es'])
    
        if self.player.erases_remaining > 0 and len(self.opponent.cards) > 0:
                last_card = self.opponent.cards[-1]
                self.handle_input('eo', self.player)
                
                eo_val = self.minimax(MINIMIZER, depth + 1)
                
                self.opponent.cards.append(last_card)
                self.player.erases_remaining += 1
                scores.append([eo_val[0], 'eo'])
    
        sorted_scores = sorted(scores, key=itemgetter(0), reverse=True)
        return sorted_scores[0]
    
    def minimizer(self, depth):
        if self.opponent.has_stopped:
            val = self.minimax(MAXIMIZER, depth + 1)
            return [val[0], 's']
        
        scores = []
        
        if len(self.deck) > 0:
            self.handle_input('d', self.opponent)

            draw_val = self.minimax(MAXIMIZER, depth + 1)

            self.deck.insert(0, self.opponent.cards.pop())
            self.seen_cards.pop()
            scores.append([draw_val[0], 'd'])

        if not self.opponent.has_stopped:
            self.handle_input('s', self.opponent)
            
            stop_val = self.minimax(MAXIMIZER, depth + 1)

            self.opponent.has_stopped = False
            scores.append([stop_val[0], 's'])

        if self.opponent.erases_remaining > 0:
            if len(self.opponent.cards) > 0:
                last_card = self.opponent.cards[-1]
                self.handle_input('es', self.opponent)

                es_val = self.minimax(MAXIMIZER, depth + 1)

                self.opponent.cards.append(last_card)
                self.opponent.erases_remaining += 1
                scores.append([es_val[0], 'es'])

        if self.opponent.erases_remaining > 0:
            if len(self.player.cards) > 0:
                last_card = self.player.cards[-1]
                self.handle_input('eo', self.opponent)

                eo_val = self.minimax(MAXIMIZER, depth + 1)

                self.player.cards.append(last_card)
                self.opponent.erases_remaining += 1
                scores.append([eo_val[0], 'eo'])

        sorted_scores = sorted(scores, key=itemgetter(0), reverse=False)
        return sorted_scores[0]
    
    def maximizer_alphabeta(self, depth, alpha, beta):
        if self.player.has_stopped:
            val = self.alphabeta(MAXIMIZER, depth + 1, alpha, beta)
            alpha = max(val[0], alpha)
            return [val[0], 's']

        scores = []
        
        if len(self.deck) > 0:
            self.handle_input('d', self.player)
            
            draw_val = self.alphabeta(MINIMIZER, depth + 1, alpha, beta)
            
            self.deck.insert(0, self.player.cards.pop())
            self.seen_cards.pop()
            
            scores.append([draw_val[0], 'd'])
            scores.sort(key=itemgetter(0), reverse=True)
            alpha = max(alpha, scores[0][0])
            if alpha >= beta:
                return scores[0]

        if not self.player.has_stopped:
            self.handle_input('s', self.player)
            
            stop_val = self.alphabeta(MINIMIZER, depth + 1, alpha, beta)
            
            self.player.has_stopped = False
            
            scores.append([stop_val[0], 's'])
            scores.sort(key=itemgetter(0), reverse=True)
            alpha = max(alpha, scores[0][0])
            if alpha >= beta:
                return scores[0]

        if self.player.erases_remaining > 0 and len(self.player.cards) > 0:
            last_card = self.player.cards[-1]
            self.handle_input('es', self.player)
            
            es_val = self.alphabeta(MINIMIZER, depth + 1, alpha, beta)
            
            self.player.cards.append(last_card)
            self.player.erases_remaining += 1
            
            scores.append([es_val[0], 'es'])
            scores.sort(key=itemgetter(0), reverse=True)
            alpha = max(alpha, scores[0][0])
            if alpha >= beta:
                return scores[0]

        if self.player.erases_remaining > 0 and len(self.opponent.cards) > 0:
                last_card = self.opponent.cards[-1]
                self.handle_input('eo', self.player)
                
                eo_val = self.alphabeta(MINIMIZER, depth + 1, alpha, beta)
                
                self.opponent.cards.append(last_card)
                self.player.erases_remaining += 1
                
                scores.append([eo_val[0], 'eo'])
                scores.sort(key=itemgetter(0), reverse=True)
                alpha = max(alpha, scores[0][0])
                if alpha >= beta:
                    return scores[0]
        
        scores.sort(key=itemgetter(0), reverse=True)
        return scores[0]

    def minimizer_alphabeta(self, depth, alpha, beta):
        if self.opponent.has_stopped:
            val = self.alphabeta(MAXIMIZER, depth + 1, alpha, beta)
            beta = min(beta, val[0])
            return [val[0], 's']
        
        scores = []
        
        if len(self.deck) > 0:
            self.handle_input('d', self.opponent)

            draw_val = self.alphabeta(MAXIMIZER, depth + 1, alpha, beta)

            self.deck.insert(0, self.opponent.cards.pop())
            self.seen_cards.pop()
            
            scores.append([draw_val[0], 'd'])
            scores.sort(key=itemgetter(0), reverse=False)
            beta = min(beta, scores[0][0])
            if alpha >= beta:
                return scores[0]

        if not self.opponent.has_stopped:
            self.handle_input('s', self.opponent)
            
            stop_val = self.alphabeta(MAXIMIZER, depth + 1, alpha, beta)

            self.opponent.has_stopped = False
            
            scores.append([stop_val[0], 's'])
            scores.sort(key=itemgetter(0), reverse=False)
            beta = min(beta, scores[0][0])
            if alpha >= beta:
                return scores[0]

        if self.opponent.erases_remaining > 0 and len(self.opponent.cards) > 0:
            last_card = self.opponent.cards[-1]
            self.handle_input('es', self.opponent)

            es_val = self.alphabeta(MAXIMIZER, depth + 1, alpha, beta)

            self.opponent.cards.append(last_card)
            self.opponent.erases_remaining += 1
            
            scores.append([es_val[0], 'es'])
            scores.sort(key=itemgetter(0), reverse=False)
            beta = min(beta, scores[0][0])
            if alpha >= beta:
                return scores[0]
        
        if self.opponent.erases_remaining > 0 and len(self.player.cards) > 0:
            last_card = self.player.cards[-1]
            self.handle_input('eo', self.opponent)

            eo_val = self.alphabeta(MAXIMIZER, depth + 1, alpha, beta)

            self.player.cards.append(last_card)
            self.opponent.erases_remaining += 1
            
            scores.append([eo_val[0], 'eo'])
            scores.sort(key=itemgetter(0), reverse=False)
            beta = min(beta, scores[0][0])
            if alpha >= beta:
                return scores[0]
        
        scores.sort(key=itemgetter(0), reverse=False)
        return scores[0]

    def minimax(self, mm_turn, depth):
        if (self.player.has_stopped and self.opponent.has_stopped) or len(self.deck) == 0:
            return [self.check_for_winners(), 's']

        if depth > 6:
            return [self.check_for_winners(), 's']
        
        if mm_turn == MAXIMIZER:
            return self.maximizer(depth)
        if mm_turn == MINIMIZER:
            return self.minimizer(depth)

    def alphabeta(self, mm_turn, depth, alpha, beta):
        if (self.player.has_stopped and self.opponent.has_stopped) or len(self.deck) == 0:
            return [self.check_for_winners(), 's']

        if depth > 6:
            return [self.check_for_winners(), 's']

        if mm_turn == MAXIMIZER:
            return self.maximizer_alphabeta(depth, alpha, beta)
        if mm_turn == MINIMIZER:
            return self.minimizer_alphabeta(depth, alpha, beta)

    def get_player_input(self):
        # """TODO"""
        # print("complete me!")
        if self.evaluator == MINIMAX:
            your_input = self.minimax(MAXIMIZER, 0)[1]
        if self.evaluator == ALPHABETA:
            your_input = self.alphabeta(MAXIMIZER, 0, -2, 2)[1]
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
import time

def test(evaluator_, test_count):
    statlist = [colored('DRAW', 'yellow'),\
    colored('WIN', 'green'),\
    colored('LOSS', 'red')]

    evals = ['MINIMAX', 'ALPHABETA']

    total_time = .0
    res = []    

    print(colored('=' * 40, 'yellow'))
    print(colored(f'Running Tests for {evals[evaluator_]}', 'yellow'))
    print(colored('=' * 40, 'yellow'))

    for i in range(test_count):
        start_time = time.time()
        game = Blacksin(deck_count=21, evaluator=evaluator_)
        res.append(game.run())
        total_time += time.time() - start_time
        
        stat = statlist[res[-1]]
        length = 3 - len(str(i + 1))
        print('running test ' + ' ' * length + str(i + 1), end=', ')
        print('result is: ' + stat)

    print()
    
    perf = res.count(1) / len(res)
    print(colored(f'performance: {round(perf, 2) * 100}%', 'green'))
    print(colored(f'--- {round(total_time, 6)} seconds ---', 'green'))

test_count = 500

test(MINIMAX, test_count)
print()
test(ALPHABETA, test_count)