import numpy as np
class Environment(object):
    def __init__(self,width,height,n_inputs,n_actions,name=None):
        self.name=name
        self.board = None #the board input
        self.turn = 0
        self.done = False
        self.winner = None  # 0 still playing, 1 p1, 2 p2, 3 draw
        self.width=width
        self.height=height
        self.n_cells=n_inputs
        self.n_actions=n_actions
        self.state=None  # A single and complete representation of the state which allows it's full reconstruction
                         # this could simple be a string containing all the class variables
    def get_state(self):
        description = "You need to override the get_state method in env. It returns a single object representing the full state."
        raise Exception('method not over-ridden', __file__, description)
    def get_result(self):
        description = "You need to override the get_result method in env. It returns a single integer - 0 game still going, 1 p1wins,2p2wins 3 draw."
        raise Exception('method not over-ridden', __file__, description)
    def is_terminal(self):
        description = "You need to override the is_terminal method in env. It returns a bool indicating if game is over. Also sets winner."
        raise Exception('method not over-ridden', __file__, description)

    def set_state(self):
        description = "You need to override the setState method in env. It sets the environment based on a given state."
        raise Exception('method not over-ridden', __file__, description)

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


    def render(self):
        description = "You need to override the render method in env. It renders the board."
        raise Exception('method not over-ridden', __file__, description)

    @property
    def observation(self):
        return ''.join(''.join(x for x in y) for y in self.board)