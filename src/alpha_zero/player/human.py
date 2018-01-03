from alpha_zero.player.player_inherit_from import Player

class Human_Player(Player):
    def __init__(self,env,playing_as=1):
        Player.env=env
        self.playing_as=playing_as

        pass
    def get_move(self, board):
        while True:
            try:
                movement = input('\nEnter your movement (1, 2, 3, 4, 5, 6, 7): ')
                movement = int(movement) - 1
                legal_moves = self.env.legal_moves()
                if legal_moves[int(movement)] == 1:
                    return int(movement)
                else:
                    print("That is NOT a valid movement :(.")
            except:
                print("That is NOT a valid movement :(.")

    def newGame(self):
        pass

    def finishedGame(self,winner,board):
        pass