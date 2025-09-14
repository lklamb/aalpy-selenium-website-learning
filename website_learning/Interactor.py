from abc import abstractmethod


class Interactor:

    def __init__(self):
        pass

    @abstractmethod
    def reset_system(self):
        pass

    @abstractmethod
    def process_input_letter(self, input_letter):
        pass

    @abstractmethod
    def final_cleanup(self):
        pass

    @abstractmethod
    def get_current_url(self):
        pass

    @abstractmethod
    def configure_for_learning(self):
        pass
