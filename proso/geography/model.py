#  -*- coding: utf-8 -*-

import operator
from math import exp

PHASE_SKIP = 'PHASE_SKIP'
PHASE_PREDICT = 'PHASE_PREDICT'
PHASE_UPDATE = 'PHASE_UPDATE'


def predict(skill_asked, option_skills):
    """
    Returns the probability of correct answer.

    Args:
        skill_asked (float):
            number representing a knowledge of the given user for the asked
            item
        option_skills ([float]):
            list of numbers representing a knowledge for the options

    Returns:
        (float, [float]):
            probability of the correct answer for the asked item
            and the probabilities for the options they will be answered instead
            of the asked item
    """

    if len(option_skills) == 0:
        return (sigmoid(skill_asked), [])

    probs = map(lambda x: sigmoid(x), [skill_asked] + option_skills)
    items = 2 ** len(probs)
    asked_prob = 0
    opt_wrong_probs = [0 for i in option_skills]

    for i in range(items):
        knows = _to_binary_reverse_list(i, len(probs))
        guess_options = 1 if knows[0] else sum(map(lambda x: 1 - x, knows))
        current_prob = reduce(
            operator.mul,
            map(lambda (p, k): p if k else 1 - p, zip(probs, knows)),
            1)
        asked_prob += (1.0 / guess_options) * current_prob
        if guess_options > 1:
            for j in range(0, len(option_skills)):
                if knows[j + 1]:
                    continue
                opt_wrong_probs[j] += 1.0 / guess_options * current_prob
    return (asked_prob, opt_wrong_probs)


def sigmoid(x):
    return 1.0 / (1 + exp(-x))


def _to_binary_reverse_list(number, length):
    binary = []
    for j in range(length):
        binary.append(number % 2)
        number = number / 2
    return binary
