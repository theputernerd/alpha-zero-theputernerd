from alpha_zero.agent.player_connect4 import Connect4Player
from alpha_zero.lib.model_helpler import load_best_model_weight
from alpha_zero.config import PlayWithHumanConfig
from alpha_zero.player.player_inherit_from import *
from alpha_zero.agent.ai_agent import Ai_Agent
from logging import getLogger
logger = getLogger(__name__)


class Alpha_Zero_Player(Player):
    def __init__(self,config,env,playing_as):  # env,player,agent inherited from Player
        Player.env=env
        PlayWithHumanConfig().update_play_config(config.play)
        self.ai_agent = Ai_Agent(config)
        self.config=config
        self.player = Connect4Player(config, self.ai_agent)
        self.playing_as=playing_as
        self.stats={}
        self.name='alpha_zero_player'
        self.shortName='alpha'

        pass

    def load(self,config_path, weight_path,stats_path):
        val=self.ai_agent.load(config_path, weight_path)

        if val:
            try:

                self.stats=self.ai_agent.load_stats(stats_path)
                logger.debug(f"stats loaded {stats_path}")
            except:
                logger.error(f"stats not loaded from {stats_path}")
            #now load stats

        return val

    # This is the placeholder for all players
    #
    def load_best_model(self,config):
        #self.ai_agent = Ai_Agent(config)
        if not load_best_model_weight(self.ai_agent):

            raise RuntimeError("best model not found!")
        return self.ai_agent

    def get_move(self, env):
        action=self.player.action(board=env.board)
        return action

    def new_game(self):
        description = "You need to override the new_game method in player. It will be called when a new game is started, and can be used to signal to your player to reset."
        raise Exception('Player method not over-ridden', __file__, description)

    def finished_game(self, winner, env):
        description = "You need to override the finished_game method in player. It will be called when a game is finished and signal to your player the winner and final board."
        raise Exception('Player method not over-ridden', __file__, description)