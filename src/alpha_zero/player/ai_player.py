from alpha_zero.agent.player_connect4 import Connect4Player
from alpha_zero.lib.model_helpler import load_best_model_weight
from alpha_zero.config import PlayWithHumanConfig
from alpha_zero.player.player_inherit_from import *

class Alpha_Zero_Player(Player):
    def __init__(self,config,env,playing_as):  # env,player,agent inherited from Player
        Player.env=env
        PlayWithHumanConfig().update_play_config(config.play)
        model = self._load_model(config)
        self.config=config
        self.player = Connect4Player(config, model)
        self.playing_as=playing_as


        pass
    # This is the placeholder for all players
    #
    def _load_model(self,config):
        from alpha_zero.agent.model_connect4 import Connect4Model
        model = Connect4Model(config)
        if not load_best_model_weight(model):
            raise RuntimeError("best model not found!")
        return model

    def get_move(self, env):
        action=self.player.action(board=env.board)
        return action
        description = "You need to override the do_move method in player. It needs to return an integer representing the move chosen based on the given board."
        raise Exception('Player method not over-ridden', __file__, description)

    def new_game(self):
        description = "You need to override the new_game method in player. It will be called when a new game is started, and can be used to signal to your player to reset."
        raise Exception('Player method not over-ridden', __file__, description)

    def finished_game(self, winner, env):
        description = "You need to override the finished_game method in player. It will be called when a game is finished and signal to your player the winner and final board."
        raise Exception('Player method not over-ridden', __file__, description)