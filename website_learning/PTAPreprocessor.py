from aalpy.learning_algs.general_passive.GsmNode import GsmNode
from aalpy.learning_algs.general_passive.GsmNode import TransitionInfo

import website_learning.Util as Util
import website_learning.Settings as Settings
from website_learning.Constants import NOT_ON_CURRENT_PAGE_STR, BOUNDARY_OF_SCOPE_STR, DEAD_END_STR, SLASH, \
    RESULTS_DIRECTORY_NAME, GO_SINK_STR, STAY_SINK_STR, outputs_without_page_change
from website_learning.Enums import InputEnabledHandling, PassiveApproach


class PTAProcessor:
    def __init__(self):
        return

    def __call__(self, root: GsmNode) -> GsmNode:
        nodes = root.get_all_nodes()
        if len(nodes) < 100:
            root.visualize(Util.base_dir / RESULTS_DIRECTORY_NAME / "PTA_before_preprocessing")  # this is slow, only for small systems
            Util.logger.info(str(len(nodes)) + " nodes, visualized PTA before preprocessing")
        else:
            Util.logger.info(str(len(nodes)) + " nodes, PTA before preprocessing not visualized for efficiency")
        if not Settings.passive_approach == PassiveApproach.PTA_PREPROCESSING:
            return root

        for node in nodes:
            if node.predecessor is None:
                current_page = Util.initial_url
            else:
                current_page = node.prefix_access_pair[1]
            if current_page in outputs_without_page_change:
                continue
            for letter in Util.input_alphabet:
                if letter.startswith(current_page):
                    continue  # these transitions already exist
                elif current_page not in Util.urls_in_scope:
                    child_node = GsmNode((letter, BOUNDARY_OF_SCOPE_STR + current_page), node)
                    node.transitions[letter] = {BOUNDARY_OF_SCOPE_STR + current_page: TransitionInfo(child_node, 1, child_node, 1)}
                elif not Util.webpage_has_interactive_elements[current_page]:
                    child_node = GsmNode((letter, DEAD_END_STR + current_page), node)
                    node.transitions[letter] = {DEAD_END_STR + current_page: TransitionInfo(child_node, 1, child_node, 1)}
                else:
                    if Settings.input_enabled_handling == InputEnabledHandling.SELF_LOOP:
                        child_output = NOT_ON_CURRENT_PAGE_STR
                    else:
                        child_output = GO_SINK_STR
                    child_node = GsmNode((letter, child_output), node)
                    node.transitions[letter] = {child_output: TransitionInfo(child_node, 1, child_node, 1)}
                    Util.logger.debug("added a new child node for " + child_output)
                    if Settings.input_enabled_handling == InputEnabledHandling.SINK_STATE:
                        for inp in Util.input_alphabet:
                            grandchild_node = GsmNode((inp, STAY_SINK_STR), child_node)
                            child_node.transitions[inp] = {STAY_SINK_STR: TransitionInfo(grandchild_node, 1, grandchild_node, 1)}
                            Util.logger.debug("added a new grandchild node for " + STAY_SINK_STR)
        nodes = root.get_all_nodes()
        if len(nodes) < 100:
            root.visualize(Util.base_dir / RESULTS_DIRECTORY_NAME / "PTA_after_preprocessing")  # this is slow, only for small systems
            Util.logger.info(str(len(nodes)) + " nodes, visualized PTA after preprocessing")
        else:
            Util.logger.info(str(len(nodes)) + " nodes, PTA after preprocessing not visualized for efficiency")
        return root

