import hashlib
import json
import os
from logging import getLogger
# noinspection PyPep8Naming
import keras.backend as K

from keras.engine.topology import Input
from keras.engine.training import Model
from keras.layers.convolutional import Conv2D
from keras.layers.core import Activation, Dense, Flatten
from keras.layers.merge import Add
from keras.layers.normalization import BatchNormalization
from keras.losses import mean_squared_error
from keras.regularizers import l2

from alpha_zero.config import Config
import logging
logger = getLogger(__name__)
logger.setLevel(logging.INFO)


class Ai_Agent:
    def __init__(self, config: Config):
        self.config = config
        self.model = None  # type: Model
        self.digest = None
        self.total_steps=0
        self.stats={}
        self.stats['total_steps'] = 0

    def build(self):
        mc = self.config.model
        in_x = x = Input((2, 6, 7))  # [own(8x8), enemy(8x8)]

        # (batch, channels, height, width)
        x = Conv2D(filters=mc.cnn_filter_num, kernel_size=mc.cnn_filter_size, padding="same",
                   data_format="channels_first", kernel_regularizer=l2(mc.l2_reg))(x)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)

        for _ in range(mc.res_layer_num):
            x = self._build_residual_block(x)

        res_out = x
        # for policy output
        x = Conv2D(filters=2, kernel_size=1, data_format="channels_first", kernel_regularizer=l2(mc.l2_reg))(res_out)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)
        x = Flatten()(x)
        # no output for 'pass'
        policy_out = Dense(self.config.n_labels, kernel_regularizer=l2(mc.l2_reg), activation="softmax", name="policy_out")(x)

        # for value output
        x = Conv2D(filters=1, kernel_size=1, data_format="channels_first", kernel_regularizer=l2(mc.l2_reg))(res_out)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)
        x = Flatten()(x)
        x = Dense(mc.value_fc_size, kernel_regularizer=l2(mc.l2_reg), activation="relu")(x)
        value_out = Dense(1, kernel_regularizer=l2(mc.l2_reg), activation="tanh", name="value_out")(x)

        self.model = Model(in_x, [policy_out, value_out], name="connect4_model")

    def _build_residual_block(self, x):
        mc = self.config.model
        in_x = x
        x = Conv2D(filters=mc.cnn_filter_num, kernel_size=mc.cnn_filter_size, padding="same",
                   data_format="channels_first", kernel_regularizer=l2(mc.l2_reg))(x)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)
        x = Conv2D(filters=mc.cnn_filter_num, kernel_size=mc.cnn_filter_size, padding="same",
                   data_format="channels_first", kernel_regularizer=l2(mc.l2_reg))(x)
        x = BatchNormalization(axis=1)(x)
        x = Add()([in_x, x])
        x = Activation("relu")(x)
        return x

    @staticmethod
    def fetch_digest(weight_path):
        if os.path.exists(weight_path):
            m = hashlib.sha256()
            with open(weight_path, "rb") as f:
                m.update(f.read())
            return m.hexdigest()

    def load(self, config_path, weight_path):

        if os.path.exists(config_path) and os.path.exists(weight_path):
            logger.info(f"loading model from {config_path}")
            try:  ##TODO: THere might be a thread clash with the file if another thread is moving the file at the time it is trying to be loaded. Need to check a few different places
                with open(config_path, "rt") as f:
                    self.model = Model.from_config(json.load(f))
            except:
                logger.error("line 89 ai_agent.py!!!!!!!!!!!!!!!!!!!!!Error loading model file")
            try:

                self.model.load_weights(weight_path)
                self.digest = self.fetch_digest(weight_path)

            except:
                logger.error("line 95 ai_agent.py!!!!!!!!!!!!!!!!!!!Error loading weights")

            logger.debug(f"loaded model digest = {self.digest}")


            return True
        else:
            logger.debug(f"model files does not exist at {config_path} and {weight_path}")
            return False

    def load_stats(self,filename):

        with open(filename, 'r') as f:
            self.stats=json.load( f)
            return self.stats
            pass

    def save_stats(self,filename):

        self.stats['total_steps']=self.total_steps

        with open(filename, 'w') as f:
            json.dump(self.stats, f)

    def save(self, config_path, weight_path,stats_path):
        logger.debug(f"save model to {config_path}")
        with open(config_path, "wt") as f:
            json.dump(self.model.get_config(), f)
            self.model.save_weights(weight_path)
        self.digest = self.fetch_digest(weight_path)
        logger.debug(f"saved model digest {self.digest}")
        self.save_stats(stats_path)



def objective_function_for_policy(y_true, y_pred):
    # can use categorical_crossentropy??
    return K.sum(-y_true * K.log(y_pred + K.epsilon()), axis=-1)


def objective_function_for_value(y_true, y_pred):
    return mean_squared_error(y_true, y_pred)
