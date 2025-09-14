from aalpy import StatePrefixEqOracle, RandomWalkEqOracle, run_Lstar

from website_learning import Settings, Util
from website_learning.Enums import EqOracleType


def active_learning(sul):
    # instantiate equivalence oracle
    eq_oracle = None
    match Settings.equivalence_oracle:
        case EqOracleType.STATE_PREFIX:
            eq_oracle = StatePrefixEqOracle(Util.input_alphabet, sul, walks_per_state=Settings.walks_per_state,
                                            walk_len=Settings.walk_len, depth_first=Settings.depth_first)
        case EqOracleType.RANDOM_WALK:
            eq_oracle = RandomWalkEqOracle(Util.input_alphabet, sul, num_steps=Settings.num_steps,
                                           reset_prob=Settings.reset_prob)

    try:
        # run the learning algorithm
        learned_model, learning_stats = run_Lstar(Util.input_alphabet, sul, eq_oracle, automaton_type='mealy',
                                                  cache_and_non_det_check=True,
                                                  print_level=2, return_data=True)

        # document results
        nr_transitions_without_selfloops = Util.save_and_visualize(learned_model)
        Util.write_learning_statistics_to_file(learning_stats)

    except SystemExit as e:
        Util.logger.error(e.code)

    sul.final_cleanup()
    return learned_model, nr_transitions_without_selfloops
    