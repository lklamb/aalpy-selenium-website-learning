from aalpy import load_automaton_from_file

import website_learning.Settings as Settings
import website_learning.Util as Util
from website_learning.Constants import outputs_without_page_change
from website_learning.Interactor import Interactor


class AutomatonInteractor(Interactor):
    def __init__(self):
        super().__init__()
        self.automaton = None
        self.current_url = None

    def configure_for_learning(self):
        with open(Settings.automaton_file_path, "r") as file:
            for line in file.readlines():
                if line.count("/") > 1:
                    Util.logger.error("In- and/or Outputs contain /s, parsing failed!\n")
                    assert False
        self.automaton = load_automaton_from_file(Settings.automaton_file_path, 'mealy')
        Util.logger.info("loaded automaton from file")

    def reset_system(self):
        self.automaton.reset_to_initial()
        self.current_url = Util.initial_url

    def process_input_letter(self, input_letter):
        output = self.automaton.step(input_letter)
        if all(not output.startswith(string) for string in outputs_without_page_change):
            self.current_url = output
        return output

    def final_cleanup(self):
        return

    def get_current_url(self):
        return self.current_url
