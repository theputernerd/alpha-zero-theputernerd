import os
from logging import getLogger
from random import random
from time import sleep
import contextlib
from alpha_zero.agent.ai_agent import Ai_Agent
from alpha_zero.agent.player_connect4 import Connect4Player
from alpha_zero.config import Config
from alpha_zero.env.connect4_env import Connect4Env
from alpha_zero.lib import tf_util
from alpha_zero.lib.data_helper import get_next_generation_model_dirs
from alpha_zero.lib.model_helpler import save_as_best_model, load_best_model_weight
import shutil

logger = getLogger(__name__)


def start(config: Config):
    tf_util.set_session_config(per_process_gpu_memory_fraction=0.2)
    return EvaluateWorker(config).start()


class EvaluateWorker:
    def __init__(self, config: Config):
        """

        :param config:
        """
        self.config = config
        self.best_model = None

    def start(self):
        self.best_model = self.load_best_model()
        while True:
            ng_model, model_dir = self.load_next_generation_model()
            if ng_model.model!=None:
                logger.debug(f"start evaluate model {model_dir}")
                ng_is_great = self.evaluate_model(ng_model)
            else:
                logger.error(f"Couldn't Load model {model_dir}")
                if os.listdir(model_dir) == []:
                    logger.error(f"directory is empty. Removing.")
                    self.remove_model(model_dir)

                    #check if directory is empty (this could occur if the optimize worker fails


            if ng_is_great:
                logger.debug(f"New Model become best model: {model_dir}")
                save_as_best_model(ng_model)
                self.best_model = ng_model

                self.remove_model(model_dir,moveToDir=self.best_model.config.resource.history_best_dir)

            else:
                self.remove_model(model_dir,moveToDir=self.best_model.config.resource.history_other_dir)

    def evaluate_model(self, ng_model):
        results = []
        winning_rate = 0
        for game_idx in range(self.config.eval.game_num):
            # ng_win := if ng_model win -> 1, lose -> 0, draw -> None
            ng_win, white_is_best = self.play_game(self.best_model, ng_model)
            if ng_win is not None:
                results.append(ng_win)
                winning_rate = sum(results) / len(results)
            logger.debug(f"game {game_idx}: ng_win={ng_win} white_is_best_model={white_is_best} "
                         f"winning rate {winning_rate*100:.1f}%")
            if results.count(0) >= self.config.eval.game_num * (1-self.config.eval.replace_rate):
                logger.debug(f"lose count reach {results.count(0)} so give up challenge")
                break
            if results.count(1) >= self.config.eval.game_num * self.config.eval.replace_rate:
                logger.debug(f"win count reach {results.count(1)} so change best model")
                break

        l = len(results)
        winning_rate = 0 if l == 0 else (sum(results) / l)  # TODO: Check this for an error. I got  a divide by zero error.
        logger.debug(f"winning rate {winning_rate*100:.1f}%")
        return winning_rate >= self.config.eval.replace_rate

    def play_game(self, best_model, ng_model):
        env = Connect4Env()
        env.reset()
        best_player = Connect4Player(self.config, best_model, play_config=self.config.eval.play_config)
        ng_player = Connect4Player(self.config, ng_model, play_config=self.config.eval.play_config)
        best_is_white = random() < 0.5
        if not best_is_white:
            black, white = best_player, ng_player
        else:
            black, white = ng_player, best_player

        env.reset()
        while not env.done:
            if env.player_turn() == 2:
                action = black.action(env.board)
            else:
                action = white.action(env.board)
            env.step(action)

        ng_win = None
        if env.winner == 1:
            if best_is_white:
                ng_win = 0
            else:
                ng_win = 1
        elif env.winner == 2:
            if best_is_white:
                ng_win = 1
            else:
                ng_win = 0
        return ng_win, best_is_white

    def load_best_model(self):
        model = Ai_Agent(self.config)
        load_best_model_weight(model)
        return model

    def load_next_generation_model(self):
        rc = self.config.resource
        while True:
            dirs = get_next_generation_model_dirs(self.config.resource)
            if dirs:
                break
            logger.info(f"There is no next generation model to evaluate")
            sleep(60)
        model_dir = dirs[-1] if self.config.eval.evaluate_latest_first else dirs[0]
        config_path = os.path.join(model_dir, rc.model_name)
        weight_path = os.path.join(model_dir, rc.model_weights_name)
        stats_path = os.path.join(model_dir, rc.model_stats_name)

        ai_agent = Ai_Agent(self.config)
        ai_agent.load(config_path, weight_path)

        return ai_agent, model_dir

    def copyDirectory(self,src, dest):
        try:
            shutil.copytree(src, dest)
        # Directories are the same
        except shutil.Error as e:
            print('Directory not copied. Error: %s' % e)
        # Any error saying that the directory doesn't exist
        except OSError as e:
            print('Directory not copied. Error: %s' % e)

    def remove_model(self, model_dir,moveToDir=None): #historyDir if you want to retain this model.
        rc = self.config.resource
        config_path = os.path.join(model_dir, rc.model_name)
        weight_path = os.path.join(model_dir, rc.model_weights_name)
        stats_path = os.path.join(model_dir, rc.model_stats_name)
        if moveToDir!= None :
            modelName=os.path.basename(os.path.normpath(model_dir))
            moveToDir=os.path.abspath(moveToDir+"\\"+modelName)
            logger.debug(f"Copying from {model_dir} to {moveToDir}")
            self.copyDirectory(model_dir,moveToDir)
        try :
            os.remove(config_path)
            os.remove(weight_path)
            os.remove(stats_path)

            os.rmdir(model_dir)
        except PermissionError as e:
            logger.error("PermissionError line 150 evaluate.py. Can't remove from {model_dir}")
            count=0
            while True:
                if count >10 : raise e

                sleep(10)
                try:
                    with contextlib.suppress(FileNotFoundError): #one of the files might not bexist now.
                        os.remove(config_path)
                        os.remove(weight_path)
                        os.remove(stats_path)
                        os.rmdir(model_dir)
                except PermissionError as e:
                    pass

                count+=1
