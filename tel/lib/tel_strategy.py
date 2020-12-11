from collections import defaultdict
import csv

from lib.enums import TELState, TELStrategy

# Multi-level map representing a markov process for each strategy China could adopt.
# { strategy (TELStrategy) ->
#     { current_state (TELState) -> 
#         { next_state (TELState) -> transition_probability (float) } } }
def load_strategies(filename):
    strategies = defaultdict(dict)
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            d = {}
            for state in TELState:
                d[state] = float(row[state.name])
            strategy = TELStrategy[row['strategy']]
            current_state = TELState[row['current_state']]
            strategies[strategy][current_state] = d
    strategies = dict(strategies)
    validate_strategies(strategies)
    return strategies
    
def validate_strategies(strategies):
    for strategy in TELStrategy:
        assert strategy in strategies, "{} not in strategies".format(strategy)
        transitions = strategies[strategy]
        for state in TELState:
            assert state in transitions, "{} not in {}".format(state, strategy)
            assert sum(transitions[state].values()) == 1, (
                "Probabilities for {} in {} don't sum to 1: {}".format(
                    state, strategy, transitions[k]))