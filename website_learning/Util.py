import os
import shutil
from copy import deepcopy
from datetime import datetime
import logging
from pathlib import Path

import yaml

import website_learning.Settings as Settings
from website_learning.WebsiteURLs import (CarAlarmWebsite, TestWebsite, RunningExample, HoverExample,
                                          MovingElementsExample, OutputExample, WebsiteURLs, TestWebsiteIndex,
                                          TestWebsiteBasics, TestWebsiteMapAreas, TestWebsiteDropdowns,
                                          TestWebsiteCheckboxes, TestWebsiteSelectionsChoices,
                                          TestWebsiteAttributeCombinations, TestWebsiteTabsWindows)
from website_learning.Constants import SEPARATOR_NEWLINE, SEPARATOR_BASIC, RESULTS_DIRECTORY_NAME, PATH_LOG, \
    PATH_INPUT_ALPHABET, PATH_SCOPE, PATH_SCOPE_BOUNDARY, MODEL_DIRECTORY_NAME, AUTOMATON_TO_LEARN_FILE_NAME, \
    PATH_INPUT_TRACES, PATH_IO_TRACES, SLASH, PATH_LM_ORIG_WITH_SL, PATH_LM_ORIG_NO_SL, PATH_LM_CLEAN_WITH_SL, \
    PATH_LM_CLEAN_NO_SL, SLASH_REPLACEMENT
from website_learning.results_cleanup import save_model_without_selfloops, cleanup_model
from website_learning.Enums import (EqOracleType, LearningType, SystemSource, DemoWebsite,
                                         InputEnabledHandling, PassiveApproach)

input_alphabet = []
initial_url = None
urls_in_scope = set()
scope_boundary = set()
webpage_has_interactive_elements = {}
number_of_resets = 0
number_of_interactions = 0
base_dir = Path(__file__).parent
logger = logging.getLogger("logger")


def init_logging():
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    logger.addHandler(console_handler)
    file_handler = logging.FileHandler(base_dir / PATH_LOG)
    logger.addHandler(file_handler)


def set_logging_level(level):
    for handler in logger.handlers:
        handler.setLevel(level)


def end_logging():
    for handler in list(logger.handlers):
        handler.close()
        logger.removeHandler(handler)
    logging.shutdown()


def write_input_alphabet_to_file():
    with open(base_dir / PATH_INPUT_ALPHABET, "w") as file:
        for letter in input_alphabet:
            file.write(letter + "\n")


def add_scope_boundary_to_file(found_boundary):
    with open(base_dir / PATH_SCOPE_BOUNDARY, "a") as file:
        file.write(found_boundary + "\n")


def write_scope_to_file():
    with open(base_dir / PATH_SCOPE, "w") as file:
        for url in urls_in_scope:
            file.write(url + "\n")


def write_learning_statistics_to_file(learning_stats):
    with open(base_dir / PATH_LOG, "a") as file:
        file.write(SEPARATOR_NEWLINE)
        file.write('Learning Finished.\n')
        file.write('Learning Rounds:  {}\n'.format(learning_stats['learning_rounds']))
        file.write('Number of states: {}\n'.format(learning_stats['automaton_size']))
        file.write('Time (in seconds)\n')
        file.write('  Total                : {}\n'.format(learning_stats['total_time']))
        file.write('  Learning algorithm   : {}\n'.format(learning_stats['learning_time']))
        file.write('  Conformance checking : {}\n'.format(learning_stats['eq_oracle_time']))
        file.write('Learning Algorithm\n')
        file.write(' # Membership Queries  : {}\n'.format(learning_stats['queries_learning']))
        if 'cache_saved' in learning_stats.keys():
            file.write(' # MQ Saved by Caching : {}\n'.format(learning_stats['cache_saved']))
        file.write(' # Steps               : {}\n'.format(learning_stats['steps_learning']))
        file.write('Equivalence Query\n')
        file.write(' # Membership Queries  : {}\n'.format(learning_stats['queries_eq_oracle']))
        file.write(' # Steps               : {}\n'.format(learning_stats['steps_eq_oracle']))
        file.write(SEPARATOR_NEWLINE)


def store_results(marker=None):
    if Settings.create_pdfs:
        if os.name == 'nt':  # WINDOWS
            ret_val = os.system('taskkill /im Acrobat.exe /f')  # close Acrobat process so that pdfs can be copied
            if ret_val == 128:
                logger.info("Acrobat was not running")
            elif ret_val != 0:
                logger.error("Acrobat could not be closed")
        else:
            logger.info("Not on Windows, could not close Acrobat")

    now = datetime.now()
    type_str = ""
    match Settings.learning_type:
        case LearningType.ACTIVE:
            type_str = "A_"
        case LearningType.PASSIVE:
            type_str = "P_"
    match Settings.system_source:
        case SystemSource.FROM_BROWSER:
            marker = marker.replace("https://", "")
            marker = marker.replace("http://", "")
            marker = marker.replace("/", "_")
        case SystemSource.FROM_AUTOMATON_FILE:
            marker = "automaton-file"

    source_folder = base_dir / RESULTS_DIRECTORY_NAME
    destination_folder = base_dir / Settings.store_dir / f"{type_str}{now.strftime("%Y-%m-%d_%H-%M-%S_")}{marker}"
    shutil.copytree(source_folder, destination_folder)

    if Settings.system_source == SystemSource.FROM_AUTOMATON_FILE:
        with open(Settings.automaton_file_path, 'r') as file:
            lines = file.readlines()
        updated_lines = []
        for line in lines:
            if line.strip().startswith('digraph '):
                updated_lines.append('digraph automaton_to_learn {\n')
            else:
                updated_lines.append(line)
        dst_path = os.path.join(destination_folder, AUTOMATON_TO_LEARN_FILE_NAME)
        with open(dst_path, 'w') as new_file:
            new_file.writelines(updated_lines)


def delete_old_results():
    folder_path = base_dir / RESULTS_DIRECTORY_NAME / MODEL_DIRECTORY_NAME
    delete_files_in_folder(folder_path)
    folder_path = base_dir / RESULTS_DIRECTORY_NAME
    delete_files_in_folder(folder_path)


def delete_files_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename == ".gitkeep":
            continue
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)


def log_settings():
    logger.info("SETTINGS")
    logger.info(SEPARATOR_BASIC)
    logger.info("Initial URL: " + Settings.website_to_learn.initial_url)
    logger.info("Scope: ")
    for url in Settings.website_to_learn.urls_in_scope[1:]:
        logger.info("  " + url)
    logger.info("Input Enabled Handling: " + str(Settings.input_enabled_handling.name))
    logger.info("Look for hover triggers: " + str(Settings.include_hover))
    logger.info("Cursor Visualisation: " + str(Settings.display_cursor))
    logger.info(SEPARATOR_BASIC)
    logger.info("SYSTEM SOURCE: " + str(Settings.system_source.name))
    match Settings.system_source:
        case SystemSource.FROM_BROWSER:
            logger.info("  Implicit Wait Time: " + str(Settings.wait_time))
        case SystemSource.FROM_AUTOMATON_FILE:
            logger.info("  Automaton File Path: " + str(Settings.automaton_file_path))
    match Settings.learning_type:
        case LearningType.ACTIVE:
            logger.info("ACTIVE LEARNING")
            logger.info("  Equivalence Oracle: " + str(Settings.equivalence_oracle.name))
            match Settings.equivalence_oracle:
                case EqOracleType.STATE_PREFIX:
                    logger.info("  Number of random walks from each state: " + str(Settings.walks_per_state))
                    logger.info("  Length of these random walks: " + str(Settings.walk_len))
                    logger.info("  Newest states are explored first (depth first): " + str(Settings.depth_first))
                case EqOracleType.RANDOM_WALK:
                    logger.info(
                        "  Maximum number of random steps that will be performed to find a counter example: " + str(
                            Settings.num_steps))
                    logger.info("  Probability that the system will be reset after a step (start new query): " + str(
                        Settings.reset_prob))
        case LearningType.PASSIVE:
            logger.info("PASSIVE LEARNING")
            logger.info("  Length of Traces: " + str(Settings.trace_len))
            logger.info("  Approach: " + str(Settings.passive_approach.name))
    logger.info(SEPARATOR_NEWLINE)


def log_time():
    logger.info("\nTIME STAMP")
    logger.info(SEPARATOR_BASIC)
    now = datetime.now()
    logger.info(now.strftime("%Y-%m-%d %H:%M:%S"))
    logger.info(SEPARATOR_NEWLINE)


def log_stats(learned_model, nr_transitions_without_selfloops, gsm_logger=None):
    logger.info("\nSTATS")
    logger.info(SEPARATOR_BASIC)
    logger.info("Total number of system resets: " + str(number_of_resets))
    logger.info("Total number of system interactions: " + str(number_of_interactions))
    logger.info("Number of found states: " + str(learned_model.size))
    logger.info("Number of transitions excluding self-loops: " + str(nr_transitions_without_selfloops))
    if gsm_logger is not None:
        logger.info("Number of node merges: " + str(gsm_logger.log_merge_count))
        logger.info("Number of node promotions: " + str(gsm_logger.log_promote_count))
    logger.info(SEPARATOR_NEWLINE)


def save_and_visualize(learned_model):
    learned_model.save(base_dir / PATH_LM_ORIG_WITH_SL)
    nr_transitions_without_selfloops = save_model_without_selfloops(base_dir / PATH_LM_ORIG_WITH_SL,
                                                                    base_dir / PATH_LM_ORIG_NO_SL)
    if Settings.create_pdfs:
        learned_model.visualize(base_dir / PATH_LM_ORIG_WITH_SL, display_same_state_transitions=True)
        learned_model.visualize(base_dir / PATH_LM_ORIG_NO_SL, display_same_state_transitions=False)
    # fix race condition while visualization threads are still working and model is already being modified
    clean_learned_model = deepcopy(learned_model)
    cleanup_model(clean_learned_model)
    clean_learned_model.save(base_dir / PATH_LM_CLEAN_WITH_SL)
    save_model_without_selfloops(base_dir / PATH_LM_CLEAN_WITH_SL, base_dir / PATH_LM_CLEAN_NO_SL)
    if Settings.create_pdfs:
        clean_learned_model.visualize(base_dir / PATH_LM_CLEAN_WITH_SL, display_same_state_transitions=True)
        clean_learned_model.visualize(base_dir / PATH_LM_CLEAN_NO_SL, display_same_state_transitions=False)
    return nr_transitions_without_selfloops


def write_input_traces_to_file(input_traces):
    with open(base_dir / PATH_INPUT_TRACES, "w") as file:
        counter = 1
        for trace in input_traces:
            file.write("INPUT TRACE " + str(counter) + "\n")
            for step in trace:
                file.write(step + "\n")
            counter += 1
            file.write("\n")
    logger.info("input traces written to file")


def write_io_traces_to_file(io_traces):
    with open(base_dir / PATH_IO_TRACES, "a") as file:
        counter = 1
        for trace in io_traces:
            file.write("\nIO TRACE " + str(counter) + "\n\n")
            for step in trace:
                file.write("IN:  " + step[0] + "\nOUT: " + step[1] + "\n\n")
            counter += 1
            file.write(SEPARATOR_NEWLINE)
    logger.info("io traces written to file")


def make_url_safe_for_display(url):
    if Settings.system_source == SystemSource.FROM_BROWSER and url.count(SLASH_REPLACEMENT) > 0:
        logger.error(url + " contains " + SLASH_REPLACEMENT + ", choose a different replacement")
        assert False
    url = url.replace(SLASH, SLASH_REPLACEMENT)
    return url


def make_url_safe_for_interaction(url):
    return url.replace(SLASH_REPLACEMENT, SLASH)


def load_config(config_path):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    website_to_learn = config["website_to_learn"]
    if isinstance(website_to_learn, str):
        try:
            website_to_learn = DemoWebsite(website_to_learn.upper())
            match website_to_learn:
                case DemoWebsite.TEST_WEBSITE:
                    Settings.website_to_learn = TestWebsite()
                case DemoWebsite.TEST_WEBSITE_INDEX:
                    Settings.website_to_learn = TestWebsiteIndex()
                case DemoWebsite.TEST_WEBSITE_BASICS:
                    Settings.website_to_learn = TestWebsiteBasics()
                case DemoWebsite.TEST_WEBSITE_MAP_AREAS:
                    Settings.website_to_learn = TestWebsiteMapAreas()
                case DemoWebsite.TEST_WEBSITE_DROPDOWNS:
                    Settings.website_to_learn = TestWebsiteDropdowns()
                case DemoWebsite.TEST_WEBSITE_CHECKBOXES:
                    Settings.website_to_learn = TestWebsiteCheckboxes()
                case DemoWebsite.TEST_WEBSITE_SELECTIONS_CHOICES:
                    Settings.website_to_learn = TestWebsiteSelectionsChoices()
                case DemoWebsite.TEST_WEBSITE_ATTRIBUTE_COMBINATIONS:
                    Settings.website_to_learn = TestWebsiteAttributeCombinations()
                case DemoWebsite.TEST_WEBSITE_TABS_WINDOWS:
                    Settings.website_to_learn = TestWebsiteTabsWindows()
                case DemoWebsite.CAR_ALARM:
                    Settings.website_to_learn = CarAlarmWebsite()
                case DemoWebsite.RUNNING_EXAMPLE:
                    Settings.website_to_learn = RunningExample()
                case DemoWebsite.HOVER_EXAMPLE:
                    Settings.website_to_learn = HoverExample()
                case DemoWebsite.MOVING_ELEMENTS_EXAMPLE:
                    Settings.website_to_learn = MovingElementsExample()
                case DemoWebsite.OUTPUT_EXAMPLE:
                    Settings.website_to_learn = OutputExample()
        except ValueError:
            logger.error("Demo not found, either choose a valid demo website_to_learn or define "
                         "website_to_learn.initial_url and website_to_learn.urls_in_scope")
            assert False
    else:
        Settings.website_to_learn = WebsiteURLs(website_to_learn["initial_url"], website_to_learn["urls_in_scope"])

    Settings.learning_type = LearningType(config["learning_type"].upper())
    Settings.system_source = SystemSource(config.get("system_source", "FROM_BROWSER").upper())
    Settings.input_enabled_handling = InputEnabledHandling(config["input_enabled_handling"].upper())
    Settings.include_hover = config.get("include_hover", True)
    Settings.display_cursor = config.get("display_cursor", False)
    match Settings.system_source:
        case SystemSource.FROM_BROWSER:
            Settings.wait_time = config.get("wait_time", 0.0)
        case SystemSource.FROM_AUTOMATON_FILE:
            Settings.automaton_file_path = config["automaton_file_path"]  # used for testing and debugging only
    match Settings.learning_type:
        case LearningType.ACTIVE:
            Settings.equivalence_oracle = EqOracleType(config.get("equivalence_oracle", "STATE_PREFIX"))
            match Settings.equivalence_oracle:
                case EqOracleType.STATE_PREFIX:
                    Settings.walks_per_state = config["walks_per_state"]
                    Settings.walk_len = config["walk_len"]
                    Settings.depth_first = config["depth_first"]
                case EqOracleType.RANDOM_WALK:
                    Settings.num_steps = config["num_steps"]
                    Settings.reset_prob = config["reset_prob"]
        case LearningType.PASSIVE:
            Settings.trace_len = config["trace_len"]
            Settings.passive_approach = PassiveApproach(config["passive_approach"].upper())
    Settings.logging_level = config.get("logging_level", "INFO")
    Settings.store_results = config.get("store_results", False)
    Settings.store_dir = config.get("store_dir", "StoredResults/")
    Settings.seed = config.get("seed", None)
    Settings.create_pdfs = config.get("create_pdfs", True)
    Settings.headless = config.get("headless", False)
