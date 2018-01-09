from alpha_zero.config import Config
from alpha_zero.agent.ai_agent import Ai_Agent

class Connect4ModelAPI:
    def __init__(self, config: Config, agent_model:Ai_Agent):
        self.config = config
        self.agent_model = agent_model




