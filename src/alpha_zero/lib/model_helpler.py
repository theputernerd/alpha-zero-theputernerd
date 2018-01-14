from logging import getLogger

logger = getLogger(__name__)


def load_best_model_weight(ai_agent):
    """

    :param alpha_zero.agent.model.ChessModel model:
    :return:
    """
    val= ai_agent.load(ai_agent.config.resource.model_best_config_path, ai_agent.config.resource.model_best_weight_path,
                       ai_agent.config.resource.model_best_stats_path,wait=False)
    try:
        pass #logger.debug("loading stats")
        #ai_agent.stats=ai_agent.load_stats(ai_agent.config.resource.model_best_stats_path)

    except:
        raise
        pass

    return val


def save_as_best_model(ai_agent):
    """

    :param alpha_zero.agent.model.ChessModel model:
    :return:
    """
    return ai_agent.save(ai_agent.config.resource.model_best_config_path, ai_agent.config.resource.model_best_weight_path,ai_agent.config.resource.model_best_stats_path)

def reload_best_model_weight_if_changed(ai_agent):
    """

    :param alpha_zero.agent.model.ChessModel model:
    :return:
    """
    logger.debug(f"start reload the best model if changed")
    digest = ai_agent.fetch_digest(ai_agent.config.resource.model_best_weight_path)
    if digest != ai_agent.digest:
        return load_best_model_weight(ai_agent)

    logger.debug(f"the best model is not changed")
    return False
