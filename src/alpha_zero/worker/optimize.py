import os
from datetime import datetime
from logging import getLogger
from time import sleep

import keras.backend as K
import numpy as np
from keras.optimizers import SGD

from connect4_zero.agent.model_connect4 import Connect4Model, objective_function_for_policy, \
    objective_function_for_value
from connect4_zero.config import Config
from connect4_zero.lib import tf_util
from connect4_zero.lib.data_helper import get_game_data_filenames, read_game_data_from_file, \
    get_next_generation_model_dirs
from connect4_zero.lib.model_helpler import load_best_model_weight
from connect4_zero.env.connect4_env import Connect4Env, Player
import json

logger = getLogger(__name__)


def start(config: Config):
    tf_util.set_session_config(per_process_gpu_memory_fraction=0.59)
    return OptimizeWorker(config).start()


class OptimizeWorker:
    def __init__(self, config: Config):
        self.config = config
        self.model = None  # type: Connect4Model
        self.loaded_filenames = set()
        self.loaded_data = {}
        self.dataset = None
        self.optimizer = None
        self.total_steps=self.config.trainer.start_total_steps
        self.stats={'total_steps':self.total_steps,}

    def start(self):
        self.model = self.load_model()
        self.training()

    def training(self):
        self.compile_model()
        last_load_data_step = last_save_step = self.total_steps #= self.config.trainer.start_total_steps
        min_data_size_to_learn = 10000
        self.load_play_data()
        #total_steps=self.total_steps

        while True:
            if self.dataset_size < min_data_size_to_learn:
                logger.info(f"dataset_size={self.dataset_size} is less than {min_data_size_to_learn}")
                sleep(60)
                self.load_play_data()
                continue
            self.update_learning_rate(self.total_steps)
            steps = self.train_epoch(self.config.trainer.epoch_to_checkpoint)
            self.total_steps += steps
            if last_save_step + self.config.trainer.save_model_steps < self.total_steps:
                self.save_current_model(steps=self.total_steps)
                last_save_step = self.total_steps

            if last_load_data_step + self.config.trainer.load_data_steps < self.total_steps:
                self.load_play_data()
                last_load_data_step = self.total_steps

    def train_epoch(self, epochs):
        tc = self.config.trainer
        state_ary, policy_ary, z_ary = self.dataset
        self.model.model.fit(state_ary, [policy_ary, z_ary],
                             batch_size=tc.batch_size,
                             epochs=epochs)
        steps = (state_ary.shape[0] // tc.batch_size) * epochs
        return steps

    def compile_model(self):
        self.optimizer = SGD(lr=1e-2, momentum=0.9)
        losses = [objective_function_for_policy, objective_function_for_value]
        self.model.model.compile(optimizer=self.optimizer, loss=losses)

    def update_learning_rate(self, total_steps):
        # The deepmind paper says
        # ~400k: 1e-2
        # 400k~600k: 1e-3
        # 600k~: 1e-4
        #TODO: Place experience annealing here.
        if total_steps < 100000:
            lr = 1e-2
        elif total_steps < 500000:
            lr = 1e-3
        elif total_steps < 900000:
            lr = 1e-4
        else:
            lr = 2.5e-5  # means (1e-4 / 4): the paper batch size=2048, ours is 512.
        K.set_value(self.optimizer.lr, lr)
        logger.debug(f"total step={total_steps}, set learning rate to {lr}")

    def save_current_model(self,steps=None):
        rc = self.config.resource
        if steps==None:
            steps=""
        else:
            steps="_"+str(steps)
        model_id = datetime.now().strftime("%Y%m%d-%H%M%S.%f")+steps
        model_dir = os.path.join(rc.next_generation_model_dir, rc.next_generation_model_dirname_tmpl % model_id)
        os.makedirs(model_dir, exist_ok=True)
        config_path = os.path.join(model_dir, rc.next_generation_model_config_filename)
        weight_path = os.path.join(model_dir, rc.next_generation_model_weight_filename)
        stats_path= os.path.join(model_dir, rc.next_generation_model_stats_filename)

        self.model.save(config_path, weight_path)
        self.save_stats(stats_path)



    def collect_all_loaded_data(self):
        state_ary_list, policy_ary_list, z_ary_list = [], [], []
        for s_ary, p_ary, z_ary_ in self.loaded_data.values():
            state_ary_list.append(s_ary)
            policy_ary_list.append(p_ary)
            z_ary_list.append(z_ary_)

        state_ary = np.concatenate(state_ary_list)
        policy_ary = np.concatenate(policy_ary_list)
        z_ary = np.concatenate(z_ary_list)
        return state_ary, policy_ary, z_ary

    @property
    def dataset_size(self):
        if self.dataset is None:
            return 0
        return len(self.dataset[0])

    def save_stats(self,filename):
        self.stats['total_steps']=self.total_steps

        with open(filename, 'w') as f:
            json.dump(self.stats, f)

    def load_stats(self,filename):
        try:
            with open(filename, 'r') as f:
                self.stats=json.load(f)
                self.total_steps=self.stats['total_steps']
        except:
            logger.debug(f"stats not loaded from {filename}")
            self.stats['total_steps']=self.total_steps
            self.total_steps=self.stats['total_steps']
        pass

    def load_model(self):
        from connect4_zero.agent.model_connect4 import Connect4Model
        model = Connect4Model(self.config)
        rc = self.config.resource

        dirs = get_next_generation_model_dirs(rc)

        if not dirs:
            logger.debug(f"loading best model")
            if not load_best_model_weight(model):
                raise RuntimeError(f"Best model can not loaded!")
            stats_path = rc.model_best_stats_path
            self.load_stats(stats_path)
        ###################

        else:
            #TODO: Why does this load the latest and not the best?
            latest_dir = dirs[-1]
            logger.debug(f"loading latest model")
            config_path = os.path.join(latest_dir, rc.next_generation_model_config_filename)
            weight_path = os.path.join(latest_dir, rc.next_generation_model_weight_filename)
            stats_path=os.path.join(latest_dir, rc.next_generation_model_stats_filename)
            model.load(config_path, weight_path)
            self.load_stats(stats_path)

        return model

    def load_play_data(self):
        filenames = get_game_data_filenames(self.config.resource)
        updated = False
        for filename in filenames:
            if filename in self.loaded_filenames:
                continue
            self.load_data_from_file(filename)
            updated = True

        for filename in (self.loaded_filenames - set(filenames)):
            self.unload_data_of_file(filename)
            updated = True

        if updated:
            logger.debug("updating training dataset")
            self.dataset = self.collect_all_loaded_data()

    def load_data_from_file(self, filename):
        try:
            logger.debug(f"loading data from {filename}")
            data = read_game_data_from_file(filename)
            self.loaded_data[filename] = self.convert_to_training_data(data)
            self.loaded_filenames.add(filename)
        except Exception as e:
            logger.warning(str(e))

    def unload_data_of_file(self, filename):
        logger.debug(f"removing data about {filename} from training set")
        self.loaded_filenames.remove(filename)
        if filename in self.loaded_data:
            del self.loaded_data[filename]

    @staticmethod
    def convert_to_training_data(data):
        """

        :param data: format is SelfPlayWorker.buffer
        :return:
        """
        state_list = []
        policy_list = []
        z_list = []
        for state, policy, z in data:
            board = list(state)
            board = np.reshape(board, (6, 7))
            env = Connect4Env().update(board)

            black_ary, white_ary = env.black_and_white_plane()
            state = [black_ary, white_ary] if env.player_turn() == Player.black else [white_ary, black_ary]

            state_list.append(state)
            policy_list.append(policy)
            z_list.append(z)

        return np.array(state_list), np.array(policy_list), np.array(z_list)