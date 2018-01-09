from logging import getLogger

logger = getLogger(__name__)


def load_best_model_weight(ai_agent):
    """

    :param alpha_zero.agent.model.ChessModel model:
    :return:
    """
    val=ai_agent.load(ai_agent.config.resource.model_best_config_path, ai_agent.config.resource.model_best_weight_path)
    try:
        ai_agent.stats=ai_agent.load_stats(ai_agent.config.resource.model_best_stats_path)
    except:
        pass

    return val


def save_as_best_model(model):
    """

    :param alpha_zero.agent.model.ChessModel model:
    :return:
    """
    return model.save(model.config.resource.model_best_config_path, model.config.resource.model_best_weight_path,model.config.resource.model_best_stats_path)

def reload_best_model_weight_if_changed(model):
    """

    :param alpha_zero.agent.model.ChessModel model:
    :return:
    """
    logger.debug(f"start reload the best model if changed")
    digest = model.fetch_digest(model.config.resource.model_best_weight_path)
    if digest != model.digest:
        return load_best_model_weight(model)

    logger.debug(f"the best model is not changed")
    return False
