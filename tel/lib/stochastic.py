from dataclasses import field
import math
from numpy import random
from lib.simulation import run

def bound(n, lower, upper):
    if n < lower:
        n = lower
    if n > upper:
        n = upper
    return n

def normal(mean, stddev, lower_bound=0, upper_bound=math.inf):
    """Sample value from a normal distribution.
    
    Values are clipped to within the specified bounds (useful to make sure
    probabilities are valid, speeds are >0, etc.)"""
    def sample():
        n = random.normal(mean, stddev)
        return bound(n, lower_bound, upper_bound)
    return field(default_factory=sample)

def uniform(low, high):
    """Sample value from a uniform distribution."""
    return field(default_factory=lambda: random.uniform(low, high))

def linear(start, inc, lower_bound=0, upper_bound=math.inf):
    """Start at start, and then increment by inc for each successive trial.
    
    If inc is a negative number, the value will decrease instead.
    Values are clipped to within the specified bounds."""
    next_value = start
    def increment():
        nonlocal next_value
        ret = next_value
        next_value = bound(next_value + inc, lower_bound, upper_bound)
        return ret
    return field(default_factory=increment)

def multiplicative(start, mult, lower_bound=0, upper_bound=math.inf):
    """Start at start, and then multiply by mult for each successive trial.
    
    For example, mult=1.1 means the value would grow by 10% each round.
    mult=0.9 would make it shrink by 10% instead.

    Values are clipped to within the specified bounds."""
    next_value = start
    def multiply():
        nonlocal next_value
        ret = next_value
        next_value = bound(next_value * mult, lower_bound, upper_bound)
        return ret
    return field(default_factory=multiply)
    
def run_stochastic(BaseConfig, output_name, iterations=10):
    c = BaseConfig(output_dir='output/{}/{:02d}'.format(output_name, 1))
    print("Iteration 1")
    print("Initial config:")
    print(c)
    print()
    run(c)
    for i in range(2, iterations+1):
        new_c = BaseConfig(output_dir='output/{}/{:02d}'.format(output_name, i))
        print("Iteration", i)
        for k, v in new_c.__dict__.items():
            if c.__dict__[k] != v:
                print("Parameter {} updated to {}".format(k, v))
        c = new_c
        print()
        run(c)