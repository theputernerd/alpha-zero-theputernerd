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
    PlayWithHumanConfig().update_play_config(config.play)
    env = Connect4Env().reset()
    alphaPlayer=Alpha_Zero_Player(config,env,2)
    its=2000
    m_Player=MCTSPlayer(env,playing_as=1,iterations=its)
    games=AIwins=Mwins=draws=0
    print(f"playing games {its}")
    while True:
        env = Connect4Env().reset()
        alphaPlayer.playing_as = 3 - m_Player.playing_as
        while not env.done:
            t=env.player_turn()
            if t == m_Player.playing_as:
                #m=env.get_legal_moves()

                print(": m",end='', flush=True)
                with Timer() as t:
                    action = m_Player.get_move(env.clone())
                print(f"{action}({round(t.interval)}s)",end='')

            elif t ==alphaPlayer.playing_as:
                print(": a",end='', flush=True)
                with Timer() as t:
                    action = alphaPlayer.get_move(env.clone())
                print(f"{action}({round(t.interval,2)}s)",end='')
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
        elif env.winner==m_Player.playing_as:
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
        elif env.winner == 3:
            p="OX"[alphaPlayer.playing_as-1]
            print(p)

        print("----------------------------------------------------------")
        print(f"{AIwins},{Mwins},{draws},{games}. {(AIwins+draws)/games}")
        print("----------------------------------------------------------")

        m_Player.playing_as = alphaPlayer.playing_as

