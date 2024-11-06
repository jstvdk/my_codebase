import random

# Card Class
class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
    
    def __str__(self):
        return f"{self.rank} of {self.suit}"
    
    def value(self):
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11
        else:
            return int(self.rank)

# Deck Class
class Deck:
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in self.suits for rank in self.ranks]
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def draw_card(self):
        return self.cards.pop() if self.cards else None

# Hand Class
class Hand:
    def __init__(self):
        self.cards = []
    
    def add_card(self, card):
        if card:
            self.cards.append(card)
    
    def calculate_score(self):
        score = 0
        aces = 0
        for card in self.cards:
            score += card.value()
            if card.rank == 'A':
                aces += 1
        while score > 21 and aces:
            score -= 10
            aces -= 1
        return score
    
    def __str__(self):
        return ', '.join(str(card) for card in self.cards) + f" (Score: {self.calculate_score()})"

# Player Base Class
class Player:
    def __init__(self, name):
        self.name = name
        self.hand = Hand()
    
    def take_card(self, card):
        self.hand.add_card(card)
    
    def show_hand(self):
        print(f"{self.name}'s Hand: {self.hand}")
    
    def calculate_score(self):
        return self.hand.calculate_score()
    
    def decide_action(self):
        raise NotImplementedError("This method should be overridden by subclasses.")

# Dealer Class
class Dealer(Player):
    def __init__(self):
        super().__init__(name="Dealer")
    
    def decide_action(self):
        score = self.calculate_score()
        if score < 17:
            return "hit"
        else:
            return "stand"

# HumanPlayer Class
class HumanPlayer(Player):
    def __init__(self, name):
        super().__init__(name)
    
    def decide_action(self):
        while True:
            action = input(f"{self.name}, do you want to (h)it or (s)tand? ").lower()
            if action in ['h', 's']:
                return "hit" if action == 'h' else "stand"
            else:
                print("Invalid input. Please enter 'h' or 's'.")

# Game Class
class Game:
    def __init__(self, players):
        self.deck = Deck()
        self.deck.shuffle()
        self.players = players  # List of Player objects
        self.dealer = Dealer()
    
    def initial_deal(self):
        for _ in range(2):
            for player in self.players:
                player.take_card(self.deck.draw_card())
            self.dealer.take_card(self.deck.draw_card())
    
    def play_turn(self, player):
        while True:
            player.show_hand()
            action = player.decide_action()
            if action == "hit":
                card = self.deck.draw_card()
                if card:
                    print(f"{player.name} hits and receives {card}.")
                    player.take_card(card)
                    if player.calculate_score() > 21:
                        print(f"{player.name} busts!")
                        break
                else:
                    print("No more cards in the deck!")
                    break
            else:
                print(f"{player.name} stands.")
                break
    
    def play_dealer_turn(self):
        self.dealer.show_hand()
        while True:
            action = self.dealer.decide_action()
            if action == "hit":
                card = self.deck.draw_card()
                if card:
                    print(f"Dealer hits and receives {card}.")
                    self.dealer.take_card(card)
                    if self.dealer.calculate_score() > 21:
                        print("Dealer busts!")
                        break
                else:
                    print("No more cards in the deck!")
                    break
            else:
                print("Dealer stands.")
                break
    
    def determine_winner(self):
        dealer_score = self.dealer.calculate_score()
        print(f"\nDealer's final score: {dealer_score}")
        for player in self.players:
            player_score = player.calculate_score()
            print(f"\n{player.name}'s final score: {player_score}")
            if player_score > 21:
                print(f"{player.name} busts and loses.")
            elif dealer_score > 21:
                print(f"Dealer busts. {player.name} wins!")
            elif player_score > dealer_score:
                print(f"{player.name} wins!")
            elif player_score == dealer_score:
                print(f"{player.name} ties with the dealer.")
            else:
                print(f"{player.name} loses.")
    
    def play_game(self):
        self.initial_deal()
        # Show dealer's first card
        print(f"\nDealer shows: {self.dealer.hand.cards[0]}")
        # Player turns
        for player in self.players:
            self.play_turn(player)
        # Dealer turn
        self.play_dealer_turn()
        # Determine winner
        self.determine_winner()

# Main Function to Run the Game
def main():
    print("Welcome to Blackjack!")
    player_name = input("Enter your name: ")
    player = HumanPlayer(player_name)
    players = [player]
    game = Game(players)
    game.play_game()

if __name__ == "__main__":
    main()