import logging
from website_learning.Enums import EqOracleType, InputEnabledHandling, LearningType, SystemSource, PassiveApproach
import website_learning.WebsiteURLs as DemoWebsite

# GENERAL SETTINGS
website_to_learn: DemoWebsite = None
learning_type: LearningType = None
system_source: SystemSource = None
input_enabled_handling: InputEnabledHandling = None  # how to handle input letters that are not on the current page
include_hover: bool = False   # BOOL, defines if hover interactions should be looked for
display_cursor: bool = False  # cursor visualisation on/off

# SETTINGS IF LEARNING FROM BROWSER
wait_time: float = None           # FLOAT, how long to wait for an element to be found

# SETTINGS IF LEARNING FROM AUTOMATON FILE
# ATTENTION: needs to match website_to_learn, only use .dot files with original in/output strings
automaton_file_path: str = None
# created with self loop
# ./automaton-files/self-loop_caralarm-6436a48_orig_withSL.dot
# ./automaton-files/self-loop_running-example_orig_withSL.dot
# created with sink state
# ./automaton-files/sink-state_running-example_orig_withSL.dot

# ACTIVE LEARNING SETTINGS
equivalence_oracle: EqOracleType = None  # equivalence oracle to use during L* algorithm
# settings for StatePrefixEqOracle
walks_per_state: int = None     # UINT
walk_len: int = None          # UINT
depth_first: bool = None     # BOOL
# settings for RandomWalkEqOracle
num_steps: int = None     # UINT
reset_prob: float = None      # FLOAT 0.0 - 1.0

# PASSIVE LEARNING SETTINGS
trace_len: int = None
passive_approach: PassiveApproach = None

# OUTPUT SETTINGS
# logging level determines output to console and files
logging_level: logging = None  # DEBUG < INFO < WARNING < ERROR < CRITICAL
# settings for output files
store_results: bool = None     # BOOL
store_dir: str = None

seed = None
create_pdfs = None
headless = None