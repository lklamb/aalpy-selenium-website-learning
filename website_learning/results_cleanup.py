from copy import deepcopy

from website_learning.Constants import (LEARNED_MODEL_FILE_NAME,
                                        NO_SELF_LOOPS_STR)
from website_learning.replacement_strings import (replacement_input_strings,
                                                  replacement_output_strings)


def cleanup_model(learned_model):
    """
    Replace strings in the learned modell for easier readability.
    Args:
      learned_model: The model to be cleaned up
    """
    for state in learned_model.states:
        state.transitions = cleanup_input(state.transitions)
        state.output_fun = cleanup_input(state.output_fun)
        state.output_fun = cleanup_output(state.output_fun)


def cleanup_input(old_dict):
    """
    Clean up input strings in the model.
    Args:
      old_dict: Transitions to be cleaned up

    Returns:
        Transitions after cleanup
    """
    new_dict = deepcopy(old_dict)
    for key in old_dict:
        for old_string in replacement_input_strings:
            if old_string in key:
                value = new_dict.pop(key)
                new_key = key.replace(old_string, replacement_input_strings[old_string])
                new_dict[new_key] = value
                break
    return new_dict


def cleanup_output(old_dict):
    """
    Clean up output strings in the model.
    Args:
      old_dict: Transitions to be cleaned up

    Returns:
        Transitions after cleanup
    """
    new_dict = deepcopy(old_dict)
    for key in new_dict:
        for old_string in replacement_output_strings:
            if old_string in new_dict[key]:
                new_dict[key] = new_dict[key].replace(old_string, replacement_output_strings[old_string])
                break
    return new_dict


def save_model_without_selfloops(dot_with_selfloops, dest_file_path):
    """
    Save model excluding self-loops in a separate file.

    Args:
      dot_with_selfloops: .dot file containing original model
      dest_file_path: where to save the cleaned up model

    Returns:
        Total number of transitions excluding self-loops
    """
    # remove self loops
    nr_transitions_without_selfloops = 0
    dot_with_selfloops_path = dot_with_selfloops.with_suffix(".dot")
    dest_file_path_dot = dest_file_path.with_suffix(".dot")
    with open(dot_with_selfloops_path, "rt") as file:
        with open(dest_file_path_dot, "w") as no_selfloops:
            for line in file:
                tokens = line.split(" ")
                if len(tokens) > 3:
                    if tokens[0] == tokens[2]:
                        continue
                    else:
                        nr_transitions_without_selfloops += 1
                        no_selfloops.write(line)
                elif line.strip().startswith('digraph '):
                    no_selfloops.write("digraph " + LEARNED_MODEL_FILE_NAME + NO_SELF_LOOPS_STR + " {\n")
                else:
                    no_selfloops.write(line)
    nr_transitions_without_selfloops -= 1  # for start arrow
    return nr_transitions_without_selfloops
