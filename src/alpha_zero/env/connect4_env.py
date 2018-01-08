import enum
import numpy as np

from logging import getLogger
from alpha_zero.env.env_inherit_from import Environment
from copy import deepcopy,copy
logger = getLogger(__name__)

# noinspection PyArgumentList
#Winner = enum.Enum("Winner", "black white draw")

# noinspection PyArgumentList
#Player = enum.Enum("Player", "black white")
class Player :
    white=1
    black=2

class Connect4Env(Environment):
    def __init__(self):
        self.board = None
        Environment.width=7
        Environment.height=6
        Environment.n_cells=Environment.width*Environment.height
        Environment.n_actions=Environment.width
        Environment.name="Connect4_6x7"
        self.h_idx=[]
        self.v_idx=[]
        self.d_idx=[]
        self.winningMoves=[]
        self._buildHoriz4()


    def _buildHoriz4(self):
        consecutive_count = 0
        col=0
        row=0
        nInarow=4-1
        for i in range(self.height):
            for j in range(self.width):

                if (i+nInarow)<self.height :
                    idx=[(i,j),(i+1,j),(i+2,j),(i+3,j)]
                    self.v_idx.append(idx)
                    self.winningMoves.append(idx)
                if (j+nInarow)<self.width :
                    idx=[(i,j),(i,j+1),(i,j+2),(i,j+3)]
                    self.h_idx.append(idx)
                    self.winningMoves.append(idx)

                if ((j+nInarow)<self.width) and (i+nInarow)<self.height:
                    idx=[(i,j),(i+1,j+1),(i+2,j+2),(i+3,j+3)]
                    self.d_idx.append(idx)
                    self.winningMoves.append(idx)

                if ((j - nInarow) >= 0) and (i + nInarow) < self.height:
                    idx = [(i, j), (i + 1, j - 1), (i + 2, j - 2), (i + 3, j - 3)]
                    self.d_idx.append(idx)
                    self.winningMoves.append(idx)


        #self.winningMoves=self.v_idx+self.h_idx+self.d_idx
        pass
    def is_terminal(self):
        return self.done
    def get_result(self):
        return self.winner
    def reset(self):
        self.board = []
        for i in range(self.height):
            self.board.append([])
            for j in range(self.width):
                self.board[i].append(' ')
        self.turn = 0
        self.done = False
        self.winner = None
        self.resigned = False
        return self
    def clone(self):
        st=Connect4Env()
        st.board = deepcopy(self.board)
        st.turn = self.turn
        st.done = self.done
        st.winner = self.winner
        st.resigned = self.resigned
        st.name=self.name
        return st

    def update(self, board):
        self.board = np.copy(board)
        self.turn = self.turn_n()
        self.done = False
        self.winner = None
        self.resigned = False
        return self

    def turn_n(self):
        turn = 0
        for i in range(self.height):
            for j in range(self.width):
                if self.board[i][j] != ' ':
                    turn += 1

        return turn

    def player_turn(self):
        if self.turn % 2 == 0:
            return 1
        else:
            return 2

    def step(self, action):
        if action is None:
            self._resigned()
            return self.board, {}
        played=False
        for i in range(self.height):
            if self.board[i][action] == ' ':
                self.board[i][action] = ('X' if self.player_turn() == Player.white else 'O')
                played=True
                break
        if not played:
            assert False

        self.turn += 1

        self.check_for_fours()

        if self.turn >= Environment.n_cells: #had to change this from > because it didn't detect draws immediately. Potentially resulting in
            self.done = True
            if self.winner is None:
                self.winner = 3

        return self.board, {}
    def get_legal_moves(self):
        legals=self.legal_moves()
        moves=np.nonzero(legals)
        self.legalmoves=moves[0]

        return moves[0]

    def legal_moves(self): #TODO:Rename this to describe that it outputs a plane.
        legal = np.zeros(self.width)
        #with connect4 it the top cell is empty then its a valid move.
        h=self.height-1
        for j in range(self.width):
            if self.board[h][j] == ' ':
                legal[j] = 1
        #for j in range(self.width):
        #    for i in range(self.height):
        #        if self.board[i][j] == ' ':
        #            legal[j] = 1
        #            break

        return legal

    def check_equal(self,positions):
        i,j=positions[0]
        val=self.board[i][j]
        if val == ' ': return False

        for (h,w) in positions:
            if self.board[h][w]!=val: return False

        if 'X' == val:
            self.winner = 1
        else:
            self.winner = 2
        return True

    def check_for_fours(self):

        for n in self.winningMoves:
            self.done=self.check_equal(n)
            if self.done :return
        self.done=False
        #[MCTSBuild(rootnode=rootnode) for _ in range(self.iterations)]
        #self.done=self.check_equal(self.winningMoves[0])
        return
        for i in range(self.height):
            for j in range(self.width):
                if self.board[i][j] != ' ':
                    # check if a vertical four-in-a-row starts at (i, j)
                    if self.vertical_check(i, j):
                        self.done = True
                        return

                    # check if a horizontal four-in-a-row starts at (i, j)
                    if self.horizontal_check(i, j):
                        self.done = True
                        return

                    # check if a diagonal (either way) four-in-a-row starts at (i, j)
                    diag_fours = self.diagonal_check(i, j)
                    if diag_fours:
                        self.done = True
                        return

    def vertical_check(self, row, col):
        # print("checking vert")
        four_in_a_row = False
        consecutive_count = 0

        for i in range(row, self.height):
            if self.board[i][col].lower() == self.board[row][col].lower():
                consecutive_count += 1
            else:
                break

        if consecutive_count >= 4:
            four_in_a_row = True
            if 'x' == self.board[row][col].lower():
                self.winner = 1
            else:
                self.winner = 2

        return four_in_a_row

    def horizontal_check(self, row, col):
        four_in_a_row = False
        consecutive_count = 0

        for j in range(col, self.width):
            if self.board[row][j].lower() == self.board[row][col].lower():
                consecutive_count += 1
            else:
                break

        if consecutive_count >= 4:
            four_in_a_row = True
            if 'x' == self.board[row][col].lower():
                self.winner = 1
            else:
                self.winner = 2

        return four_in_a_row

    def diagonal_check(self, row, col):
        four_in_a_row = False
        count = 0

        consecutive_count = 0
        j = col
        for i in range(row, self.height):
            if j > self.height:
                break
            elif self.board[i][j].lower() == self.board[row][col].lower():
                consecutive_count += 1
            else:
                break
            j += 1

        if consecutive_count >= 4:
            count += 1
            if 'x' == self.board[row][col].lower():
                self.winner = 1
            else:
                self.winner = 2

        consecutive_count = 0
        j = col
        for i in range(row, -1, -1):
            if j > self.height:
                break
            elif self.board[i][j].lower() == self.board[row][col].lower():
                consecutive_count += 1
            else:
                break
            j += 1

        if consecutive_count >= 4:
            count += 1
            if 'x' == self.board[row][col].lower():
                self.winner = 1
            else:
                self.winner = 2

        if count > 0:
            four_in_a_row = True

        return four_in_a_row

    def _resigned(self):
        if self.player_turn() == Player.white:
            self.winner = 1
        else:
            self.winner = 2
        self.done = True
        self.resigned = True

    def black_and_white_plane(self):
        board_white = np.copy(self.board)
        board_black = np.copy(self.board)
        for i in range(self.height):
            for j in range(self.width):
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
        line1=""
        line2=""
        for i in range(self.height-1, -1, -1):
            print("\t", end="")
            for j in range(self.width):
                print("| " + str(self.board[i][j]), end=" ")
            print("|")
        for j in range(self.width):
            line1+="_   "
            line2+=f"{j}   "
        print(f"\t  {line1}")
        print(f"\t  {line2}")

        if self.done:
            print("Game Over!")
            if self.winner == 1:
                print("X is the winner")
            elif self.winner == 2:
                print("O is the winner")
            else:
                print("Game was a draw")

    @property
    def observation(self):
        return ''.join(''.join(x for x in y) for y in self.board)
