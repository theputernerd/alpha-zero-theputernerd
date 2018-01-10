import os
import time
import errno

def _project_dir():
    d = os.path.dirname
    return d(d(d(os.path.abspath(__file__))))


def _data_dir():
    return os.path.join(_project_dir(), "data")


class Config:
    def __init__(self, config_type="normal"):
        self.opts = Options()
        self.resource = ResourceConfig()

        if config_type == "mini":
            import alpha_zero.configs.mini as c
        elif config_type == "normal":
            import alpha_zero.configs.normal as c
        else:
            raise RuntimeError(f"unknown config_type: {config_type}")
        self.model = c.ModelConfig()
        self.play = c.PlayConfig()
        self.play_data = c.PlayDataConfig()
        self.trainer = c.TrainerConfig()
        self.eval = c.EvaluateConfig()

        self.n_labels = 7


class Options:
    new = False


class ResourceConfig:
    def __init__(self):
        self.project_dir = os.environ.get("PROJECT_DIR", _project_dir())
        self.data_dir = os.environ.get("DATA_DIR", _data_dir())
        self.model_dir = os.environ.get("MODEL_DIR", os.path.join(self.data_dir, "model"))
        self.model_name="model_config.json"
        self.model_weights_name="model_weight.h5"
        self.model_stats_name="model_stats.json"
        self.model_best_config_path = os.path.join(self.model_dir, self.model_name)
        self.model_best_weight_path = os.path.join(self.model_dir, self.model_weights_name)
        self.model_best_stats_path = os.path.join(self.model_dir, self.model_stats_name)

        self.next_generation_model_dir = os.path.join(self.model_dir, "next_generation")
        self.next_generation_model_dirname_tmpl = "model_%s"
        #self.next_generation_model_config_filename = self.model_name
        #self.next_generation_model_weight_filename = self.model_weights_name
        #self.next_generation_model_stats_filename = self.model_stats_name
        self.play_data_dir = os.path.join(self.data_dir, "play_data")
        self.play_data_filename_tmpl = "play_%s.json"

        self.history_best_dir=os.path.join(self.model_dir,"history_best")
        self.history_other_dir=os.path.join(self.model_dir,"history_other")
        self.zeroFolder=self.history_best_dir+"\\_0\\"
        self.tempFolder = os.path.abspath('../../temp')
        self.resultsFolder = os.path.abspath('../../results')
        self.log_dir = os.path.join(self.project_dir, "logs")
        self.main_log_path = os.path.join(self.log_dir, "main.log")
        self.maxFilestoTrainWith=50  #there is 100 games per file. #this reduces training time. For small values do only 1 epoch
        self.min_data_size_to_learn = 5000 #make sure there is enough data in each file to reach this number



    def create_directories(self,wait=True):
        #why is this so complex? So the user can decide if they want to reset everything, in case restart is unintentional.
        #to reset they just need to delete the folders. If it is not supposed to be a new run then thy can escapre the program.
        #you should only call this if the model has not loaded for some reason.

        waiting= True
        printBool=True
        hadToCreateDirs=False
        while waiting:
            try:
                dirs = [self.tempFolder, self.resultsFolder, self.zeroFolder,
                        self.play_data_dir,
                        self.next_generation_model_dir, self.history_other_dir]#folders further back are automatically created.
                for d in dirs:
                    os.makedirs(d,exist_ok=False)
                hadToCreateDirs = True
                print("dirs Made")
                waiting=False
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
                if not wait :
                    waiting=False
                else:
                    if printBool:
                        print("Error config.py line 82. These directories cannot exist, delete them to start training. Sleeping until you do ")
                        print("Be careful you only delete the existing ones and not ones I create after you have removed them. ")
                        mDirs  = [self.tempFolder, self.resultsFolder, self.data_dir]

                        for d in mDirs:
                            print (str(d))

                        printBool=False

                    time.sleep(20)
        return hadToCreateDirs


class PlayWithHumanConfig:
    def __init__(self):
        self.simulation_num_per_move = 500
        self.thinking_loop = 2
        self.logging_thinking = True
        self.c_puct = 2
        self.parallel_search_num = 32
        self.noise_eps = 0
        self.change_tau_turn = 0
        self.resign_threshold = None

    def update_play_config(self, pc):
        """

        :param PlayConfig pc:
        :return:
        """
        pc.simulation_num_per_move = self.simulation_num_per_move
        pc.thinking_loop = self.thinking_loop
        pc.logging_thinking = self.logging_thinking
        pc.c_puct = self.c_puct
        pc.noise_eps = self.noise_eps
        pc.change_tau_turn = self.change_tau_turn
        pc.parallel_search_num = self.parallel_search_num
        pc.resign_threshold = self.resign_threshold

class PlayVMCTSConfig:
    def __init__(self):
        self.simulation_num_per_move = 100
        self.thinking_loop = 10
        self.logging_thinking = True
        self.c_puct = 2
        self.parallel_search_num = 4
        self.noise_eps = 0
        self.change_tau_turn = 0
        self.resign_threshold = None

    def update_play_config(self, pc):
        """

        :param PlayConfig pc:
        :return:
        """
        pc.simulation_num_per_move = self.simulation_num_per_move
        pc.thinking_loop = self.thinking_loop
        pc.logging_thinking = self.logging_thinking
        pc.c_puct = self.c_puct
        pc.noise_eps = self.noise_eps
        pc.change_tau_turn = self.change_tau_turn
        pc.parallel_search_num = self.parallel_search_num
        pc.resign_threshold = self.resign_threshold
