class Player(object):
    def __init__(self,env):
        #This is the placeholder for all players
        self.env=env #this is the environment. It has predefined methods with the Player class calls.
    def get_move(self,board):
        description="You need to override the do_move method in player. It needs to return an integer representing the move chosen based on the given board."
        raise Exception('Player method not over-ridden',__file__,description)

    def new_game(self):
        description="You need to override the new_game method in player. It will be called when a new game is started, and can be used to signal to your player to reset."
        raise Exception('Player method not over-ridden',__file__,description)

    def finished_game(self, winner, board):
        description="You need to override the finished_game method in player. It will be called when a game is finished and signal to your player the winner and final board."
        raise Exception('Player method not over-ridden',__file__,description)