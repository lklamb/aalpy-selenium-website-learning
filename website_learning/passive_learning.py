from typing import Dict

from aalpy import MealyState, run_GSM
from aalpy.learning_algs.general_passive.GsmNode import GsmNode
from aalpy.learning_algs.general_passive.ScoreFunctionsGSM import \
    ScoreCalculation

from website_learning import Settings, Util
from website_learning.Constants import (BOUNDARY_OF_SCOPE_STR, DEAD_END_STR,
                                        GO_SINK_STR,
                                        INTERACTION_INTERCEPTED_STR,
                                        NOT_INTERACTABLE_STR,
                                        NOT_ON_CURRENT_PAGE_STR, STAY_SINK_STR,
                                        outputs_without_page_change)
from website_learning.Enums import InputEnabledHandling, PassiveApproach
from website_learning.GSMLogger import GSMLogger
from website_learning.PTAPreprocessor import PTAPreprocessor
from website_learning.TraceGenerator import TraceGenerator


def passive_learning(sul):
    """
    Executes a passive learning process on a website system.

    Args:
        sul: System Under Learning, the website to be learned

    Returns:
        learned_model: Mealy machine representation of the learned behaviour of the website
        nr_transitions_without_selfloops: Total number of transitions present in the learned model excluding all self-loops
    """
    # generate data
    trace_generator = TraceGenerator(sul)
    sul.final_cleanup()

    def custom_score(part: Dict[GsmNode, GsmNode]):  # the higher the score, the more likely to merge
        """
        Custom scoring function that penalizes merges for invalid input nodes that do not result in self-loops.
        Args:
          part: Dict[GsmNode: GsmNode]: Partitioning to be scored

        Returns:
            Score for intended merge

        """
        for old_node in part.keys():
            if len(old_node.transitions) == 0 and (
                old_node.prefix_access_pair[1] == NOT_ON_CURRENT_PAGE_STR
                or old_node.prefix_access_pair[1] == STAY_SINK_STR
                or old_node.prefix_access_pair[1] == INTERACTION_INTERCEPTED_STR
                or old_node.prefix_access_pair[1] == NOT_INTERACTABLE_STR
                or old_node.prefix_access_pair[1].startswith(BOUNDARY_OF_SCOPE_STR)
                or old_node.prefix_access_pair[1].startswith(DEAD_END_STR)
            ):
                # these nodes should only be merged with their parent -> self loop
                if part[old_node] != part[old_node.predecessor]:
                    return -1
        return 1

    def custom_compatibility(a: GsmNode, b: GsmNode):
        """
        Custom compatibility function to keep nodes on different webpages from merging.

        Args:
          a: GsmNode: First node to be checked
          b: GsmNode: Second node to be checked

        Returns:
            True if both nodes are on the same page, false otherwise.
        """
        def page(x: GsmNode):
            """
            Gets the current page of a node.

            Args:
              x: GsmNode: The node to be evaluated

            Returns:
                The current page of the node
            """
            if x.prefix_access_pair[1] is None:
                assert Util.initial_url is not None
                return Util.initial_url
            elif x.prefix_access_pair[1] in outputs_without_page_change:
                return page(x.predecessor)
            else:
                return x.prefix_access_pair[1]

        return page(a) == page(b)

    score_function = None
    compatibility_function = None
    match Settings.passive_approach:
        case PassiveApproach.PTA_PREPROCESSING:
            score_function = custom_score
        case PassiveApproach.COMPATIBILITY_FUNC:
            compatibility_function = custom_compatibility

    gsm_logger = GSMLogger()

    # run the learning algorithm
    learned_model = run_GSM(
        trace_generator.io_traces,
        output_behavior="mealy",
        transition_behavior="deterministic",
        score_calc=ScoreCalculation(score_function=score_function, local_compatibility=compatibility_function),
        pta_preprocessing=PTAPreprocessor(),
        instrumentation=gsm_logger,
    )

    if Settings.passive_approach == PassiveApproach.COMPATIBILITY_FUNC:
        # postprocessing
        learned_model.compute_prefixes()

        sink_state = None
        if Settings.input_enabled_handling == InputEnabledHandling.SINK_STATE:
            sink_state = MealyState("s" + str(len(learned_model.states)))
            for letter in Util.input_alphabet:
                sink_state.transitions[letter] = sink_state
                sink_state.output_fun[letter] = STAY_SINK_STR

        current_page = None
        for state in learned_model.states:
            if state == learned_model.initial_state:
                current_page = Util.initial_url
            else:
                output_seq = learned_model.compute_output_seq(learned_model.initial_state, state.prefix)
                current_page = output_seq[-1]
            if current_page in outputs_without_page_change:
                assert False  # shortest path should never include a self-loop
            for letter in Util.input_alphabet:
                if letter.startswith(current_page):
                    continue  # these transitions already exist
                elif current_page not in Util.urls_in_scope:
                    state.transitions[letter] = state
                    state.output_fun[letter] = BOUNDARY_OF_SCOPE_STR + current_page
                elif not Util.webpage_has_interactive_elements[current_page]:
                    state.transitions[letter] = state
                    state.output_fun[letter] = DEAD_END_STR + current_page
                else:
                    if Settings.input_enabled_handling == InputEnabledHandling.SELF_LOOP:
                        state.transitions[letter] = state
                        state.output_fun[letter] = NOT_ON_CURRENT_PAGE_STR
                    else:
                        state.transitions[letter] = sink_state
                        state.output_fun[letter] = GO_SINK_STR

        if Settings.input_enabled_handling == InputEnabledHandling.SINK_STATE:
            learned_model.states.append(sink_state)

    # document results
    nr_transitions_without_selfloops = Util.save_and_visualize(learned_model)
    return learned_model, nr_transitions_without_selfloops, gsm_logger
