import csv

from lib.enums import TimeOfDay, TELState, TELType, AlertLevel

def load_strategies(filename):
    strategies = {}
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
            strategies[(tel_type, alert_level, time_of_day, current_state)] = d
    validate_strategies(strategies)
    return strategies
    
def validate_strategies(strategies):
    for tel_type in TELType:
        for alert_level in AlertLevel:
            for tod in TimeOfDay:
                for state in TELState:
                    k = (tel_type, alert_level, tod, state)
                    assert k in strategies, "{} not in strategies".format(k)
                    assert sum(strategies[k].values()) == 1, (
                        "Probabilities for {} don't sum to 1: {}".format(
                            k, strategies[k]))