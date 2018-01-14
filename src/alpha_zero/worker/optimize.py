import os
from datetime import datetime
from logging import getLogger
from time import sleep

import keras.backend as K
import numpy as np
from keras.optimizers import SGD
import contextlib
from alpha_zero.agent.ai_agent import Ai_Agent, objective_function_for_policy, \
    objective_function_for_value
from alpha_zero.config import Config
from alpha_zero.lib import tf_util
from alpha_zero.lib.data_helper import get_game_data_filenames, read_game_data_from_file, \
    get_next_generation_model_dirs
from alpha_zero.lib.model_helpler import load_best_model_weight
from alpha_zero.env.connect4_env import Connect4Env, Player
import json
import random
import time
from threading import Thread

logger = getLogger(__name__)


def start(config: Config):
    tf_util.set_session_config(per_process_gpu_memory_fraction=0.59)
    return OptimizeWorker(config).start()


class OptimizeWorker:
    def __init__(self, config: Config):
        self.config = config
        self.ai_agent = None  # type: Ai_Agent
        self.loaded_filenames = set()
        self.files_used={}
        self.loaded_data = {}
        self.dataset = None
        self.optimizer = None

        self.doneOne=False #this flag indicates if at least 1 epoch has been done on the loaded data to inform the removal of files
        self.removedFiles=False #flags whether files have ben removed since the last data check
        logger.debug("doneOne False line43")
        self.filenames=[]
        self.steps_taken=0

    def start(self):
        #self.model = self.load_model()
        self.ai_agent=Ai_Agent(self.config)
        self.load_model_to_be_optimized()  ###TODO: IF GOING TO ALLOW MULTIPLE OPTIMIZE AGENTS THEN NEED TO PEIODICALLY LOAD best
        self.steps_taken=self.ai_agent.stats['total_steps']
        self.training()

    def training(self):
        self.compile_model()
        min_data_size_to_learn =self.config.resource.min_data_size_to_learn

        self.load_play_data()
        #total_steps=self.total_steps

        while True:
            #if self.dataset_size < min_data_size_to_learn:
            self.load_play_data()
            self.removedFiles=False
            if self.dataset_size < min_data_size_to_learn:
                logger.info(f"dataset_size={self.dataset_size} is less than {min_data_size_to_learn}")
                #run selfplay once.

                from alpha_zero.worker import self_play
                sp=self_play.SelfPlayWorker(self.config)
                sp.one_round_of_self_play(self.ai_agent)

                #sleep(60)
                self.load_play_data()
                self.doneOne=False
                logger.debug("doneOne False line65")

                continue
            logger.info(f"dataset_size={self.dataset_size}")

            if not self.removedFiles:
                self.update_learning_rate()
                logger.info(f"steps:{self.steps_taken}")

                steps = self.train_epoch(epochs=self.config.trainer.epoch_to_checkpoint)
                self.steps_taken += steps
                ###Changed to save after each training epoch.
                #if last_save_step + self.config.trainer.save_model_steps < self.total_steps:
                self.ai_agent.stats['total_steps']+=steps #=self.steps_taken
                self.save_current_model()
                #last_save_step = self.total_steps

            #if last_load_data_step + self.config.trainer.load_data_steps < self.total_steps:
            #load data everytime.
            #last_load_data_step = self.total_steps
    #TODO: PUT A DATA SPLITTER FUNCTION HERE.
    def train_epoch(self, epochs):
        tc = self.config.trainer

        state_ary, policy_ary, z_ary = self.dataset
        idx=np.argsort(np.random.random(len(state_ary)))[:self.config.resource.trainig_data_size]
        state_ary=state_ary[idx]
        policy_ary=policy_ary[idx]
        z_ary=z_ary[idx]

        logger.debug("doneOne True")
        self.doneOne = True
        self.ai_agent.model.fit(state_ary, [policy_ary, z_ary],
                             batch_size=tc.batch_size,
                             epochs=epochs)
        steps = (state_ary.shape[0] // tc.batch_size) * epochs
        return steps

    def compile_model(self):
        self.optimizer = SGD(lr=1e-2, momentum=0.9)
        losses = [objective_function_for_policy, objective_function_for_value]
        self.ai_agent.model.compile(optimizer=self.optimizer, loss=losses)

    def update_learning_rate(self):
        # The deepmind paper says
        # ~400k: 1e-2
        # 400k~600k: 1e-3
        # 600k~: 1e-4
        #TODO: Place experience annealing here.
        if self.ai_agent.stats['total_steps'] < 100000:
            lr = 1e-2
        elif self.ai_agent.stats['total_steps'] < 500000:
            lr = 1e-3
        elif self.ai_agent.stats['total_steps'] < 900000:
            lr = 1e-4
        else:
            lr = 2.5e-5  # means (1e-4 / 4): the paper batch size=2048, ours is 512.
        K.set_value(self.optimizer.lr, lr)
        logger.debug(f"total step={self.ai_agent.stats['total_steps']}, set learning rate to {lr}")

    def save_current_model(self):
        rc = self.config.resource

        steps="_"+str(self.ai_agent.stats['total_steps'])
        model_id = datetime.now().strftime("%Y%m%d-%H%M%S.%f")+steps
        model_dir = os.path.join(rc.next_generation_model_dir, rc.next_generation_model_dirname_tmpl % model_id)
        os.makedirs(model_dir, exist_ok=True)
        logger.debug(f"Saving model to {model_dir}")
        config_path = os.path.join(model_dir, rc.model_name)
        weight_path = os.path.join(model_dir, rc.model_weights_name)
        self.ai_agent.stats['date']=datetime.now().strftime("%d/%m/%Y")
        self.ai_agent.stats['time']=datetime.now().strftime("%H%M")+":"+datetime.now().strftime("%S")

        stats_path= os.path.join(model_dir, rc.model_stats_name)

        self.ai_agent.save(config_path, weight_path,stats_path)



    def collect_all_loaded_data(self):
        state_ary_list, policy_ary_list, z_ary_list = [], [], []
        ####Use a small subset of files here.
        #a=random.sample(self.loaded_data,self.config.resource.maxFilestoTrainWith)
        print("collect_all_loaded_data() optimize.py")
        for s_ary, p_ary, z_ary_ in self.loaded_data.values():
            state_ary_list.append(s_ary)
            policy_ary_list.append(p_ary)
            z_ary_list.append(z_ary_)
        if len(state_ary_list)>0:
            state_ary = np.concatenate(state_ary_list)
            policy_ary = np.concatenate(policy_ary_list)
            z_ary = np.concatenate(z_ary_list)

            return state_ary, policy_ary, z_ary
        else:
            logger.debug("doneOne False")
            self.doneOne = False
            return [],[],[]

    @property
    def dataset_size(self):
        if self.dataset is None:
            return 0
        return len(self.dataset[0])


    def load_stats(self,filename):
        try:
            with open(filename, 'r') as f:
                self.ai_agent.stats=json.load(f)
                #self.total_steps=self.stats['total_steps']
        except:
            logger.debug(f"stats not loaded from {filename}")

        pass

    def load_model_to_be_optimized(self):
        """logger.debug(f"loading best model")
        val=False
        while not val:

            val=load_best_model_weight(self.ai_agent)
            if not val:
                logger.error("Best model can not be loaded. waiting 10")
                time.sleep(10)
            #raise RuntimeError(f"Best model can not be loaded!")


        return self.ai_agent
        """
        rc = self.config.resource
        dirs = get_next_generation_model_dirs(rc)
        logger.debug(f"loading model")

        if not dirs:
            logger.debug(f"loading best model")
            val = False
            while not val:
                val = load_best_model_weight(self.ai_agent)
                if not val:
                    logger.error("Best model can not be loaded. waiting 10")
                    time.sleep(10)
        ###################

        else:
            logger.debug(f"loading latest model.")
            for i in range(len(dirs)-1):
                latest_dir = dirs[-(i+1)]
                logger.debug(f"loading latest model {latest_dir}")
                config_path = os.path.join(latest_dir, rc.model_name)
                weight_path = os.path.join(latest_dir, rc.model_weights_name)
                stats_path=os.path.join(latest_dir, rc.model_stats_name)
                try:
                    self.ai_agent.load(config_path, weight_path, stats_path)
                except FileNotFoundError:
                    logger.debug(f"model not found in {latest_dir}")

                    continue
                self.load_stats(stats_path)
                break

        return self.ai_agent

    def load_play_data(self):
        #This is where I will track how many times a file has been used to train off.
        self.removedFiles=False
        updated = False
        for filename in self.filenames:
            if filename in self.loaded_filenames:
                #if the filename is already in loaded_filenames then there is a 25% of its removal
                if self.doneOne:
                    rnum=random.random()
                    logger.debug(f"Rolling to replace:{rnum}")
                    if rnum<self.config.trainer.buffer_file_remove_prob:
                        self.removedFiles=True
                        ##remove the file
                        st=f"randomly removing file {filename} - "
                        with contextlib.suppress(FileNotFoundError):
                            os.remove(filename)

                            #t=Thread(target=os.remove,args=(filename))
                            #t.start()
                            #st+="removed"
                        updated = True
                        logger.debug(st)

                continue
            else :
                self.load_data_from_file(filename)

                updated = True

        self.filenames = get_game_data_filenames(self.config.resource)

        for filename in (self.loaded_filenames - set(self.filenames)):
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
        #TODO: Save the player as part of the data
        for state, policy, z in data:
            board = list(state)
            board = np.reshape(board, (6, 7))
            env = Connect4Env().update(board)

            black_ary, white_ary = env.black_and_white_plane()
            state = [black_ary, white_ary] if env.player_turn() == 2 else [white_ary, black_ary]

            state_list.append(state)
            policy_list.append(policy)
            z_list.append(z)

        return np.array(state_list), np.array(policy_list), np.array(z_list)
