import os
from datetime import datetime
from logging import getLogger
from time import time

from alpha_zero.agent.player_connect4 import Connect4Player
from alpha_zero.config import Config
from alpha_zero.env.connect4_env import Connect4Env
from alpha_zero.lib import tf_util
from alpha_zero.lib.data_helper import get_game_data_filenames, write_game_data_to_file
from alpha_zero.lib.model_helpler import load_best_model_weight, save_as_best_model, \
    reload_best_model_weight_if_changed
import random
logger = getLogger(__name__)
import contextlib


def start(config: Config):
    tf_util.set_session_config(per_process_gpu_memory_fraction=0.2)
    return SelfPlayWorker(config, env=Connect4Env()).start()


class SelfPlayWorker:
    def __init__(self, config: Config, env=None, ai_agent=None):
        """

        :param config:
        :param Connect4Env|None env:
        :param alpha_zero.agent.ai_agent.Ai_Agent|None model:
        """
        self.config = config
        self.ai_agent = ai_agent
        self.env = env     # type: Connect4Env
        self.black = None  # type: Connect4Player
        self.white = None  # type: Connect4Player
        self.buffer = []
        self.newRun=False  #changes to true if the model has to be built fully.
        self.fileUsageDic={} #keeps track of how many times a file has been used

    def start(self):
        if self.ai_agent is None:
            self.ai_agent = self.load_model()

        self.buffer = []
        idx = 1

        if self.newRun :
            full=False
            while not full:
                self.env.reset()
                full=self.start_rnd_game(idx)
                logger.debug(f"game {idx} "
                             f"turn={self.env.turn}:{self.env.observation} - Winner:{self.env.winner}")
                idx += 1
        logger.info(f"Now starting self play")
        while True:
            start_time = time()
            env = self.start_game(idx)
            end_time = time()
            logger.debug(f"game {idx} time={end_time - start_time} sec, "
                         f"turn={env.turn}:{env.observation} - Winner:{env.winner}")
            if (idx % self.config.play_data.nb_game_in_file) == 0:
                reload_best_model_weight_if_changed(self.ai_agent)
            idx += 1

    def start_rnd_game(self,idx):
        self.env.reset()
        self.black = Connect4Player(self.config, self.ai_agent)
        self.white = Connect4Player(self.config, self.ai_agent)
        while not self.env.done:
            action = random.choice(self.env.get_legal_moves())
            self.env.step(action)
        self.finish_game()
        self.save_play_data(write=idx % self.config.play_data.nb_game_in_file == 0)
        removed=self.remove_play_data()
        return removed

    def start_game(self, idx):
        self.env.reset()
        self.black = Connect4Player(self.config, self.ai_agent)
        self.white = Connect4Player(self.config, self.ai_agent)
        while not self.env.done:
            if self.env.player_turn() == 2:
                action = self.black.action(self.env.board)
            else:
                action = self.white.action(self.env.board)
            self.env.step(action)
        self.finish_game()
        self.save_play_data(write=idx % self.config.play_data.nb_game_in_file == 0)
        self.remove_play_data()
        return self.env

    def save_play_data(self, write=True):
        data = self.black.moves + self.white.moves
        self.buffer += data

        if not write:
            return

        rc = self.config.resource
        game_id = datetime.now().strftime("%Y%m%d-%H%M%S.%f")
        path = os.path.join(rc.play_data_dir, rc.play_data_filename_tmpl % game_id)
        logger.info(f"save play data to {path}")
        write_game_data_to_file(path, self.buffer)
        self.buffer = []

    def remove_play_data(self):

        files = get_game_data_filenames(self.config.resource)


        if len(files) < self.config.play_data.max_file_num:
            return False #didn't remove any
        for i in range(len(files) - self.config.play_data.max_file_num):
            with contextlib.suppress(FileNotFoundError): #in case we have two workers who clash during remove
                os.remove(files[i]) #removes the oldest files
                print("Removed some files")

        return True #removed some files

    def finish_game(self):
        if self.env.winner == 2:
            black_win = 1
        elif self.env.winner == 1:
            black_win = -1
        else:
            black_win = 0

        self.black.finish_game(black_win)
        self.white.finish_game(-black_win)

    def load_model(self):
        from alpha_zero.agent.ai_agent import Ai_Agent
        from shutil import copyfile
        ai_agent = Ai_Agent(self.config)
        if self.config.opts.new or not load_best_model_weight(ai_agent):
            ###NOW I NEED TO FILL THE BUFFER OR SIGNAL THAT IT NEEDS TO BE FILLED.
            self.newRun=self.config.resource.create_directories()

            ai_agent.build() #TODO: Move the make dirs into this function

            save_as_best_model(ai_agent) #since I am building a new model, the training examples don't realte to the model so delete it.

            stats = {}
            stats['total_steps'] = 0
            #self.model_best_config_path = os.path.join(self.model_dir, "model_best_config.json")
            #self.model_best_weight_path = os.path.join(self.model_dir, "model_best_weight.h5")
            #self.model_best_stats_path = os.path.join(self.model_dir, "model_best_stats.json"

            try :
                #TODO: One day fix this and just use the config variables.
                copyfile(self.config.resource.model_best_config_path,self.config.resource.history_best_dir+"\\_0\\"+self.config.resource.model_name)
                copyfile(self.config.resource.model_best_weight_path,self.config.resource.history_best_dir+"\\_0\\"+self.config.resource.model_weights_name)
                copyfile(self.config.resource.model_best_stats_path,self.config.resource.history_best_dir+"\\_0\\"+self.config.resource.model_stats_name)

                stats['total_steps'] = 0
                #filename=self.config.resource.history_best_dir + "\\_0\\" + self.config.resource.model_stats_name
                #copyfile(self.config.resource.model_best_stats_path,self.config.resource.history_best_dir+"\\"+self.config.resource.next_generation_model_stats_filename)
            except(FileNotFoundError):
                raise
                pass


        return ai_agent


