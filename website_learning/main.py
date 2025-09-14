import logging
import random
import sys
import threading

import website_learning.Settings as Settings
import website_learning.Util as Util
from website_learning.WebsiteSUL import WebsiteSUL
from website_learning.Enums import LearningType, SystemSource
from website_learning.active_learning import active_learning
from website_learning.passive_learning import passive_learning


# if chrome does not open, make sure that chromedriver.exe can get through the firewall!
def main(config_path):
    Util.delete_old_results()
    Util.init_logging()
    Util.set_logging_level(logging.ERROR)
    Util.load_config(config_path)

    # for reproducible results
    random.seed(Settings.seed)

    Util.set_logging_level(Settings.logging_level)
    Util.log_time()
    Util.log_settings()

    # instantiate the SUL
    sul = WebsiteSUL()
    if len(Util.input_alphabet) == 0:
        Util.logger.info("No interactive elements found, input alphabet is empty!")
        assert False

    if Settings.learning_type == LearningType.ACTIVE:
        learned_model, nr_transitions_without_selfloops = active_learning(sul)
        gsm_logger = None
    else:
        learned_model, nr_transitions_without_selfloops, gsm_logger = passive_learning(sul)

    # wait for visualization threads to finish
    this_thread = threading.current_thread()
    for t in threading.enumerate():
        if t is not this_thread:
            t.join()

    Util.log_time()
    Util.log_stats(learned_model, nr_transitions_without_selfloops, gsm_logger)

    try:
        if Settings.store_results:  # currently only works if using Acrobat on Windows
            if Settings.system_source == SystemSource.FROM_BROWSER:
                Util.store_results(Settings.website_to_learn.initial_url)
            else:
                Util.store_results()
    except:
        Util.logger.error("Results not stored")

    Util.end_logging()

    return learned_model, nr_transitions_without_selfloops


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python website_learning.py <config_path>")
        sys.exit(1)
    path = sys.argv[1]
    main(path)
