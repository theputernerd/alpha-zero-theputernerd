from logging import getLogger

from alpha_zero.config import Config, PlayWithHumanConfig
from alpha_zero.env.connect4_env import Connect4Env
from random import random
from alpha_zero.player.ai_player import *
from alpha_zero.player.human import *
from alpha_zero.player.mcts import MCTSPlayer
from alpha_zero.lib.helpers import Timer

logger = getLogger(__name__)

def start(config: Config):
    PlayWithHumanConfig().update_play_config(config.play)
    env = Connect4Env()
    env.reset()
    humanPlayer=Human_Player(env,playing_as=1)
    env = Connect4Env()
    env.reset()    #aiPlayer=Alpha_Zero_Player(config,env,1)
    aiPlayer=MCTSPlayer(env,playing_as=2,iterations=1000)

    while True:
        env = Connect4Env()
        env.reset()
        humanPlayer.playing_as = 3 - aiPlayer.playing_as
        while not env.done:
            t=env.player_turn()
            if t == aiPlayer.playing_as:
                with Timer() as t:
                    action = aiPlayer.get_move(env.clone())
                print(f"{action}({t.interval}s)", end='')

                print("AI moves to: " + str(action))

            elif t ==humanPlayer.playing_as:
                action = humanPlayer.get_move(env.clone())
                print("You move to: " + str(action))
            else:
                assert False #turn doesn't match a player.
            env.step(action)
            env.render()

        print("\nEnd of the game.")
        print("Game result:")
        if env.winner == 1:
            print("X wins")
        elif env.winner == 2:
            print("O wins")
        else:
            print("Game was a draw")
        aiPlayer.playing_as = humanPlayer.playing_as

