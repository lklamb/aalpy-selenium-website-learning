from typing import List

from aalpy.learning_algs.general_passive.GeneralizedStateMerging import Instrumentation, GeneralizedStateMerging, \
    Partitioning
from aalpy.learning_algs.general_passive.GsmNode import GsmNode

import website_learning.Util as Util
from website_learning.Constants import SEPARATOR_NEWLINE


class GSMLogger(Instrumentation):
    def __init__(self):
        super().__init__()
        self.log_merge_count = 0
        self.log_promote_count = 0

    def reset(self, gsm: 'GeneralizedStateMerging'):
        Util.logger.debug("reset")

    def pta_construction_done(self, root: GsmNode):
        Util.logger.info("PTA construction done")

    def log_promote(self, node: GsmNode):
        self.log_promote_count += 1
        Util.logger.debug("promoted a blue node to red (" + str(self.log_promote_count) + ")")

    def log_merge(self, part: Partitioning):
        self.log_merge_count += 1
        Util.logger.debug("merged nodes (" + str(self.log_merge_count) + ")")

    def learning_done(self, root: GsmNode, red_states: List[GsmNode]):
        Util.logger.info(SEPARATOR_NEWLINE)
        Util.logger.info("Learning finished.")
        Util.logger.info("Number of states: " + str(len(red_states)))

