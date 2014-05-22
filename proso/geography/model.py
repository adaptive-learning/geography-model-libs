#  -*- coding: utf-8 -*-

import operator
import current
import prior
from math import exp

PHASE_SKIP = 'PHASE_SKIP'
PHASE_PREDICT = 'PHASE_PREDICT'
PHASE_UPDATE = 'PHASE_UPDATE'


class AnswerStream:

    def stream_answer(self, answer):
        if not isinstance(answer, dict):
            answer = answer.__dict__
        env = self.environment()
        prior_status, prior_data = self.prior_prepare(answer, env)
        if prior_status != PHASE_SKIP:
            prior_prediction = self.prior_predict(answer, prior_data)
            self.prior_update(answer, env, prior_data, prior_prediction)
        current_status, current_data = self.current_prepare(answer, env)
        current_prediction = self.current_predict(answer, current_data)
        if current_status != PHASE_SKIP:
            self.current_update(answer, env, current_data, current_prediction)
        env.process_answer(
            answer['user'],
            answer['place_asked'],
            answer['place_answered'],
            answer['inserted'])
        if prior_status == PHASE_PREDICT:
            return prior_prediction
        else:
            return current_prediction

    def current_prepare(self, answer, env):
        raise NotImplementedError()

    def current_predict(self, answer, data):
        raise NotImplementedError()

    def current_update(self, answer, env, data, prediction):
        raise NotImplementedError()

    def environment(self):
        raise NotImplementedError()

    def prior_prepare(self, answer, env):
        raise NotImplementedError()

    def prior_predict(self, answer, data):
        raise NotImplementedError()

    def prior_update(self, answer, env, data, prediction):
        raise NotImplementedError()


class DefaultAnswerStream(AnswerStream):

    def __init__(self, env):
        self._env = env

    def current_prepare(self, answer, env):
        return current.pfa_prepare(answer, env)

    def current_predict(self, answer, data):
        return current.pfa_predict(answer, data)

    def current_update(self, answer, env, data, prediction):
        return current.pfa_update(answer, env, data, prediction)

    def environment(self):
        return self._env

    def prior_prepare(self, answer, env):
        return prior.elo_prepare(answer, env)

    def prior_predict(self, answer, data):
        return prior.elo_predict(answer, data)

    def prior_update(self, answer, env, data, prediction):
        return prior.elo_update(answer, env, data, prediction)


def predict_simple(skill_asked, number_of_options):
    guess = 0.0
    if number_of_options:
        guess = 1.0 / number_of_options
    return (guess + (1 - guess) * sigmoid(skill_asked), [])


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
