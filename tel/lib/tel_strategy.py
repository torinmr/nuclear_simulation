import csv

from lib.enums import TimeOfDay, TELState, TELType, AlertLevel

def load_strategy(filename):
    strategy = {}
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            d = {}
            for state in TELState:
                d[state] = float(row[state.name])

            tel_type = TELType[row['tel_type']]
            alert_level = AlertLevel[row['alert_level']]
            time_of_day = TimeOfDay[row['time_of_day']]
            current_state = TELState[row['current_state']]
            strategy[(tel_type, alert_level, time_of_day, current_state)] = d
    validate_strategy(strategy)
    return strategy
    
def validate_strategy(strategy):
    for tel_type in TELType:
        for alert_level in AlertLevel:
            for tod in TimeOfDay:
                for state in TELState:
                    k = (tel_type, alert_level, tod, state)
                    assert k in strategy, "{} not in strategy".format(k)
                    assert sum(strategy[k].values()) == 1, (
                        "Probabilities for {} don't sum to 1: {}".format(
                            k, strategy[k]))