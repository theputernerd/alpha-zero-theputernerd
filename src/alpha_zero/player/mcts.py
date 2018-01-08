epsilon=1e-9
from math import *
from alpha_zero.player.player_inherit_from import Player
import random
class Node:
    """ A node in the game tree. Note wins is always from the viewpoint of playerJustMoved.
        Crashes if state not specified.
    """

    def __init__(self, move=None, parent=None, state=None):
        self.move = move  # the move that got us to this node - "None" for the root node
        self.parentNode = parent  # "None" for the root node
        self.childNodes = []
        self.wins = 0
        self.visits = epsilon #this is so that we don't get a divide by 0
        self.untriedMoves = state.get_legal_moves().tolist()
        self.playerJustMoved = 3-state.player_turn()  # the only part of the state that the Node needs later
        self.UCTVal=0
        self.state=state

    def UCTSelectChild(self):
        #Selects a child state.
        s = sorted(self.childNodes, key=lambda c: c.wins / c.visits + sqrt(log(self.visits+1) / c.visits) + random.random()*epsilon)[-1]

        #random number is in case we get a tie. Might be unnecesary and wasteful in big games.
        return s

    def getUCTVal(self,player=None):
        #Return the UCT Value of this node
        if(player==None) :player=3-self.playerJustMoved

        UCTVal = self.wins / self.visits
        if(player==3-self.playerJustMoved) :#TODO: IS THIS A SOURCE OF ERROR- IS IT CORRECT TO HAVE THIS. PREVIOUSLY I MADE NO REFERENCE AS TO WHICH PLAYER WAS GETTING VALUE.Passes the MCTS tests though.
            UCTVal=1-UCTVal


        return UCTVal

    def getUCTPolicy(self):
        #returns the [Child's Move, UCTVisits, UCT values] of all the children of this node.
        UCTValues=[]
        UCTVisits=[]
        UCTMove=[]

        for c in self.childNodes :
            UCTValues.append(c.wins / c.visits)
            UCTVisits.append(c.visits)
            UCTMove.append(c.move)

        return [UCTMove,UCTVisits,UCTValues]

    def AddChild(self, m, state):
        """ Remove m from untriedMoves and add a new child node for this move.
            Return the added child node
        """
        n = Node(move=m, parent=self, state=state)
        self.untriedMoves.remove(m)
        self.childNodes.append(n)
        return n

    def Update(self, result):
        """ Update this node - one additional visit and result additional wins.
            result must be from the viewpoint of playerJustmoved.
        """
        self.visits += 1
        self.wins += result

    def __repr__(self):
        return "[M:" + str(self.move) + " W/V:" + str(self.wins) + "/" + str(self.visits) + " U:" + str(
            self.untriedMoves) + "]"

    def TreeToString(self, indent):
        s = self.IndentString(indent) + str(self)
        for c in self.childNodes:
            s += c.TreeToString(indent + 1)
        return s

    def IndentString(self, indent):
        s = "\n"
        for i in range(1, indent + 1):
            s += "| "
        return s

    def ChildrenToString(self):
        s = ""
        for c in self.childNodes:
            s += str(c) + "\n"
        return s
def GetUCTVal(game,itermax, verbose=False,player=None) :
    # Returns the UCTValue of the given state, using itermax iterations..
    rootnode = Node(state=game)

    for i in range(itermax):
       MCTSBuild(rootnode)

    return rootnode.getUCTVal(player)
def GeUCTMove(rootstate, itermax, verbose=False):
    """Gets the best move given the particular gamestate. Usually to interface with another game player you will
      need to simply convert their move into a compliant gamestate. If you have a representation in a compliant state format
      then you can use it as the roostate in this function . Return the best move from the rootstate.
    """

    rootnode = Node(state=rootstate.Clone())

    for i in range(itermax):
        MCTSBuild(rootnode)

    # Output some information about the tree
    if (verbose):
        print (rootnode.TreeToString(0))
    else:
        pass # print rootnode.ChildrenToString()

    return sorted(rootnode.childNodes, key=lambda c: c.visits)[-1].move  # return the move that was most visited

def MCTSBuild(rootnode, verbose=False) :
    #Builds the MCTS tree
    #rootnode.state.reset()

    node = rootnode
    #state = rootnode.state.Clone()

    # Select
    state=node.state.clone()

    while node.untriedMoves == [] and node.childNodes != []:
        node = node.UCTSelectChild()  #cant optimise this cause the node changes with each iteration.
        state.step(node.move)
    # Expand
    #if not node.untriedMoves == []:  # if we can expand (i.e. state/node is non-terminal) BAD error in MCTS.AI Code here.
    if not state.is_terminal():  # if we can expand (i.e. state/node is non-terminal) BAD error in MCTS.AI Code here.

        # Unlike above it is more wasteful and incorrect to expand the tree beyond terminal cause it returns bad results
        #starting with a terminal state can cause a untriedMoves to be empty.
        #TODO: Make sure the state has a move representing pass eg -1
        try :
            m = random.choice(node.untriedMoves)

            state.step(m)
            node = node.AddChild(m, state.clone())  # add child and descend tree
        except IndexError :
            pass

    # TODO: For some games there will need to be a pass option. This should reside in the gamestate. But need to ensure that both players dont pass forever.
    # Rollout -
    while not state.done:

        m=state.get_legal_moves()
        if len(m)==0 :
            print(state.render())
            print(state.winner)
            print(state.done)
            assert False #Shouldn't get here.
        a=random.choice(m)
        state.step(a)
    #state.rndPlayout()  # this is faster than a while loop in the MCTS, but if not doing RND playout then wont help.
    result = state.get_result()

    # Backpropagate
    while node != None:  # backpropagate from the expanded node and work back to the root node
        val = -1000
        if result == node.playerJustMoved:           #Since we are progressing down the tree we need to keep track of each players reward at each level.
            val = 1.0
        elif result == 3-node.playerJustMoved:
            val = 0.0
        elif result == 3:
            val = 0.5
        else :
            assert False #HOW DID YOU GET HERE??
        node.Update(val)  # state is terminal. Update node with result from POV of node.playerJustMoved
        node = node.parentNode

import numpy as np
class MCTSPlayer(Player):
    def __init__(self,env,playing_as=1,iterations=300,name="MCTS"):
        shortName="M"+str(iterations)
        super().__init__(env,playing_as,name,shortName)
        self.iterations=iterations
        self.gameplayed=0

    def newGame(self):
        pass

    def get_move(self,env):
        """Gets the best move given the particular gamestate. Usually to interface with another game player you will
          need to simply convert their move into a compliant gamestate. If you have a representation in a compliant state format
          then you can use it as the roostate in this function . Return the best move from the rootstate.
        """

        rootnode = Node(state=env)
        #Game = rootstate.Clone()

        [MCTSBuild(rootnode=rootnode) for _ in range(self.iterations)]

        return sorted(rootnode.childNodes, key=lambda c: c.visits)[-1].move  # return the move that was most visited

    def getMoveDist(self,playerPieces):
        return np.zeros_like(playerPieces)

        #return a
    def DoMove(self,env):

        m=self.GetMove(env,env.board)
        env.step(m)
    def NewGame(self):
        pass
    def GameOver(self,game):
        pass

