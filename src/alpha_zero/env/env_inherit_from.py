import numpy as np
class env(object):
    def __init__(self):

        self.board = None
        self.turn = 0
        self.done = False
        self.winner = None  # type: Winner
        self.resigned = False
        self.x=7
        self.y=6
        self.n_inputs=None
        self.n_outputs=None

    def reset(self):
        description = "You need to override the do_move method in env. It returns self."
        raise Exception('method not over-ridden', __file__, description)

    def update(self, board):
        description = "You need to override the update method in env. It updated the environment to look like board. It returns self."
        raise Exception('method not over-ridden', __file__, description)

    def turn_n(self):
        ##for connnect 4 this figures out whose turn it is - because the environment doesnt track who's turn it is.
        assert False


    def player_turn(self):
        return self.turn #how many turns have occured in the game

    def step(self, action): #take this step in the environment.
        description = "You need to override the step method in env. It updated the environment to look like board. It returns self.board,{}."
        raise Exception('method not over-ridden', __file__, description)
        return self.board, {}

    def legal_moves(self):
        description = "You need to override the legal_moves method in env. It returns a list of the legal moves."
        raise Exception('method not over-ridden', __file__, description)

        return legal


    def black_and_white_plane(self):
        board_white = np.copy(self.board)
        board_black = np.copy(self.board)
        for i in range(self.y):
            for j in range(self.x):
                if self.board[i][j] == ' ':
                    board_white[i][j] = 0
                    board_black[i][j] = 0
                elif self.board[i][j] == 'X':
                    board_white[i][j] = 1
                    board_black[i][j] = 0
                else:
                    board_white[i][j] = 0
                    board_black[i][j] = 1

        return np.array(board_white), np.array(board_black)

    def render(self):
        print("\nRound: " + str(self.turn))

        for i in range(5, -1, -1):
            print("\t", end="")
            for j in range(7):
                print("| " + str(self.board[i][j]), end=" ")
            print("|")
        print("\t  _   _   _   _   _   _   _ ")
        print("\t  1   2   3   4   5   6   7 ")

        if self.done:
            print("Game Over!")
            if self.winner == 1:
                print("X is the winner")
            elif self.winner == 2:
                print("O is the winner")
            else : #TODO: self.winner ==3
                print("Game was a draw")

    @property
    def observation(self):
        return ''.join(''.join(x for x in y) for y in self.board)