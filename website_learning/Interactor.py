from abc import abstractmethod


class Interactor:
    """ Abstract class that defines necessary interactions with and accesses to the SUL."""

    def __init__(self):
        pass

    @abstractmethod
    def reset_system(self):
        """Reset the system to its initial state. """
        pass

    @abstractmethod
    def process_input_letter(self, input_letter):
        """
        Process a single input letter.

        Args:
          input_letter: Input letter to be processed

        Returns:
          Output after the interaction
        """
        pass

    @abstractmethod
    def final_cleanup(self):
        """Cleanup after learning has ended. """
        pass

    @abstractmethod
    def get_current_url(self):
        """Get the URL the SUL is currently on. """
        pass

    @abstractmethod
    def configure_for_learning(self):
        """Configure the interactor for the learning phase. """
        pass
