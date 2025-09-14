from typing import Dict

from aalpy import run_GSM, MealyState
from aalpy.learning_algs.general_passive.GsmNode import GsmNode
from aalpy.learning_algs.general_passive.ScoreFunctionsGSM import ScoreCalculation

from website_learning import Util, Settings
from website_learning.Constants import NOT_ON_CURRENT_PAGE_STR, STAY_SINK_STR, BOUNDARY_OF_SCOPE_STR, \
    DEAD_END_STR, outputs_without_page_change, INTERACTION_INTERCEPTED_STR, NOT_INTERACTABLE_STR, GO_SINK_STR
from website_learning.Enums import PassiveApproach, InputEnabledHandling
from website_learning.GSMLogger import GSMLogger
from website_learning.PTAPreprocessor import PTAProcessor
from website_learning.TraceGenerator import TraceGenerator


def passive_learning(sul):
    # generate data
    trace_generator = TraceGenerator(sul)
    sul.final_cleanup()

    def custom_score(part: Dict[GsmNode, GsmNode]):  # the higher the score, the more likely to merge
        for old_node in part.keys():
            if (len(old_node.transitions) == 0 and
                    (old_node.prefix_access_pair[1] == NOT_ON_CURRENT_PAGE_STR or
                     old_node.prefix_access_pair[1] == STAY_SINK_STR or
                     old_node.prefix_access_pair[1] == INTERACTION_INTERCEPTED_STR or
                     old_node.prefix_access_pair[1] == NOT_INTERACTABLE_STR or
                     old_node.prefix_access_pair[1].startswith(BOUNDARY_OF_SCOPE_STR) or
                     old_node.prefix_access_pair[1].startswith(DEAD_END_STR))):
                # these nodes should only be merged with their parent -> self loop
                if part[old_node] != part[old_node.predecessor]:
                    return -1
        return 1

    def custom_compatibility(a: GsmNode, b: GsmNode):
        def page(x: GsmNode):
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
    learned_model = run_GSM(trace_generator.io_traces,
                            output_behavior='mealy',
                            transition_behavior='deterministic',
                            score_calc=ScoreCalculation(score_function=score_function,
                                                        local_compatibility=compatibility_function),
                            pta_preprocessing=PTAProcessor(),
                            instrumentation=gsm_logger)

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
