import website_learning.Util as Util
import website_learning.Settings as Settings
from website_learning.AutomatonInteractor import AutomatonInteractor
from website_learning.Constants import (BOUNDARY_OF_SCOPE_STR, DEAD_END_STR, SEPARATOR_BASIC, SEPARATOR_NEWLINE,
                                        STAY_SINK_STR, NOT_ON_CURRENT_PAGE_STR, GO_SINK_STR, DELIMITER_FOR_LETTER)
from website_learning.Enums import SystemSource, InputEnabledHandling
from website_learning.WebsiteInteractor import WebsiteInteractor

from aalpy.base import SUL


class WebsiteSUL(SUL):

    def __init__(self):
        Util.number_of_resets = 0
        Util.number_of_interactions = 0
        Util.input_alphabet = []
        Util.urls_in_scope = set()
        Util.scope_boundary = set()
        Util.webpage_has_interactive_elements = {}

        Util.logger.info("INIT")
        Util.logger.info(SEPARATOR_BASIC)
        super().__init__()
        self.sink_reached = False
        self.interactor = WebsiteInteractor()
        self.interactor.analysis_phase()  # analysis is always done on the actual website
        if Settings.system_source == SystemSource.FROM_AUTOMATON_FILE:
            self.interactor = AutomatonInteractor()
        self.interactor.configure_for_learning()
        Util.logger.info(SEPARATOR_NEWLINE)

    def pre(self):
        Util.logger.info(SEPARATOR_NEWLINE)
        Util.number_of_resets += 1
        Util.logger.info("PRE walk " + str(Util.number_of_resets))
        self.sink_reached = False
        self.interactor.reset_system()

    def post(self):
        Util.logger.info("\nPOST")

    def step(self, letter_string):
        Util.logger.info("\nSTEP")
        if letter_string is None:
            Util.logger.error("empty input letter")
            assert False
        Util.number_of_interactions += 1
        Util.logger.info("Input Letter: " + letter_string)

        if Settings.input_enabled_handling == InputEnabledHandling.SINK_STATE and self.sink_reached:
            Util.logger.debug("staying in sink state")
            Util.logger.info("Output: " + STAY_SINK_STR)
            return STAY_SINK_STR

        url_before_step = self.interactor.get_current_url()

        if url_before_step not in Util.urls_in_scope:
            Util.logger.debug(url_before_step + " is boundary of scope")
            if url_before_step not in Util.scope_boundary:
                Util.scope_boundary.add(url_before_step)
                Util.add_scope_boundary_to_file(url_before_step)
            Util.logger.info("Output: " + BOUNDARY_OF_SCOPE_STR + url_before_step)
            return BOUNDARY_OF_SCOPE_STR + url_before_step
        if not Util.webpage_has_interactive_elements.get(url_before_step):
            Util.logger.debug(url_before_step + " does not have interactive elements")
            Util.logger.info("Output: " + DEAD_END_STR + url_before_step)
            return DEAD_END_STR + url_before_step

        letter_url = letter_string.split(DELIMITER_FOR_LETTER)[0]
        if letter_url != url_before_step:
            Util.logger.debug("element to interact with is on page " + letter_url + ", currently on page "
                              + url_before_step)
            match Settings.input_enabled_handling:
                case InputEnabledHandling.SELF_LOOP:
                    Util.logger.debug("creating self loop")
                    Util.logger.info("Output: " + NOT_ON_CURRENT_PAGE_STR)
                    return NOT_ON_CURRENT_PAGE_STR
                case InputEnabledHandling.SINK_STATE:
                    self.sink_reached = True
                    Util.logger.debug("going to sink state")
                    Util.logger.info("Output: " + GO_SINK_STR)
                    return GO_SINK_STR
                case _:
                    assert False

        output = Util.make_url_safe_for_display(self.interactor.process_input_letter(letter_string))
        Util.logger.info("Output: " + output)
        return output

    def final_cleanup(self):
        self.interactor.final_cleanup()
