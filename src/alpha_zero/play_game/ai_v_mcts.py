from logging import getLogger
import logging
from alpha_zero.config import Config, PlayWithHumanConfig
from alpha_zero.env.connect4_env import Connect4Env
from random import random
from alpha_zero.player.ai_player import *
from alpha_zero.player.human import *
from alpha_zero.player.mcts import MCTSPlayer
from alpha_zero.lib.helpers import Timer

logger = getLogger(__name__)
logger.setLevel(logging.INFO)
import time

def start(config: Config):
    #env = Connect4Env().reset()
    #humanPlayer=Human_Player(env,playing_as=2)
    env = Connect4Env().reset()
    alphaPlayer=Alpha_Zero_Player(config,env,2)
    aiPlayer=MCTSPlayer(env,playing_as=1,iterations=1000)
    games=AIwins=Mwins=draws=0
    print("playing games")
    while True:
        env = Connect4Env().reset()
        alphaPlayer.playing_as = 3 - aiPlayer.playing_as
        while not env.done:
            t=env.player_turn()
            if t == aiPlayer.playing_as:
                #m=env.get_legal_moves()

                print(": m",end='', flush=True)
                with Timer() as t:
                    action = aiPlayer.get_move(env.clone())
                print(f"{action}({t.interval}s)",end='')

            elif t ==alphaPlayer.playing_as:
                print(": a",end='', flush=True)
                action = alphaPlayer.get_move(env.clone())
                print(f"{action}",end='')
            else:
                assert False #turn doesn't match a player.
            env.step(action)

            #env.render()
        print()
        games += 1
        env.render()
        if env.winner==alphaPlayer.playing_as:
            AIwins+=1
            print ("AI wins as ",end='')
        elif env.winner==MCTSPlayer.playing_as:
            Mwins+=1
            print ("MCTS wins as ",end='')

        elif env.winner==3:
            draws+=1
            print ("Draw. AI played ",end='')


        #print("\nEnd of the game.")
        #print("Game result:")
        if env.winner == 1:
            print("X")
        elif env.winner == 2:
            print("O")
        print("----------------------------------------------------------")
        print(f"{AIwins},{Mwins},{draws},{games}. {(AIwins+draws)/games}")
        print("----------------------------------------------------------")

        aiPlayer.playing_as = alphaPlayer.playing_as

