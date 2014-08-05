#  -*- coding: utf-8 -*-

import abc
import operator
import current
import prior
from math import exp

PHASE_SKIP = 'PHASE_SKIP'
PHASE_PREDICT = 'PHASE_PREDICT'
PHASE_UPDATE = 'PHASE_UPDATE'


class PredictiveModel:

    """
    This class handles handles the logic behind the predictive models, which is
    divided into 3 phases:
        prepare:
            the model loads the necessary data from the environment
        predict
            the model uses the loaded data to predict the correctness of the answer
        update
            the model updates environment to persist it for the future prediction
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def prepare(self, user_id, place_asked_id, options, question_type, inserted, environment):
        """
        In this phase, the predictive model touches the environment, loads all
        necessary data and returns it.

        Args:
            user_id (int):
                identifier of the user answering the question
            place_asked_id (int):
                identifier of the asked place
            options (list):
                list of identifier for the options (the asked place included),
                if there is no option, the question is open
            question_type (int):
                type of the question: (1) find the given place on the map; (2)
                pick the name for the highlighted place
            inserted (datetime.datetime):
                datetime when the question is answered
            environment (proso.geography.environment.Environment):
                environment where all the important data are persist

        Returns:
            object
        """
        return

    @abc.abstractmethod
    def predict(self, user_id, place_asked_id, options, question_type, inserted, data):
        """
        Uses the data from prepare phase and tries to predict the probability
        of the correct answer. That means the prediction for the user and the
        asked place before the given answer is processed.

        Args:
            user_id (int):
                identifier of the user answering the question
            place_asked_id (int):
                identifier of the asked place
            options (list):
                list of identifier for the options (the asked place included),
                if there is no option, the question is open
            question_type (int):
                type of the question: (1) find the given place on the map; (2)
                pick the name for the highlighted place
            inserted (datetime.datetime):
                datetime when the question is answered
            data (object):
                data from the prepare phase

        Returns:
            float:
                the number from [0, 1] representing the probability of the
                correct answer
        """
        return

    @abc.abstractmethod
    def update(self, answer, environment, data, prediction):
        """
        After the prediction update the environment and persist some
        information for the predictive model.

        Args:
            answer (dict):
                dict-like structure representing the answer
            environment (proso.geography.environment.Environment):
                environment where all the important data are persist
            data (object):
                data from the prepare phase
            prediction (float):
                the number from [0, 1] representing the probability of the
                correct answer
        """
        return


class AnswerStream:

    """
    This class handles stream of answer for the purpose of the predictive
    models.
    """

    def __init__(self, predictive_model, environment):
        self._predictive_model = predictive_model
        self._environment = environment

    def stream_answer(self, answer):
        """
        Handles one answer of the stream. Answer is represented as a dict-like
        structure.

        Args:
            answer (dict):
                dict-like structure with the following keys: user, place_asked,
                place_answered, response_time, inserted

        Returns:
            float: prediction of the correctness for the given answer
        """
        if not isinstance(answer, dict):
            answer = answer.__dict__
        env = self.environment()
        data = self.predictive_model().prepare(
            answer['user'],
            answer['place_asked'],
            answer['options'],
            answer['type'],
            answer['inserted'],
            env)
        prediction = self.predictive_model().predict(
            answer['user'],
            answer['place_asked'],
            answer['options'],
            answer['type'],
            answer['inserted'], data)
        self.predictive_model().update(
            answer, env, data, prediction)
        env.process_answer(
            answer['user'],
            answer['place_asked'],
            answer['place_answered'],
            answer['response_time'],
            answer['inserted'])
        return prediction

    @abc.abstractmethod
    def environment(self):
        """
        Returns an environment used by the stream.

        Returns:
            proso.geography.environment.Environment
        """
        return self._environment

    @abc.abstractmethod
    def predictive_model(self):
        """
        Returns a predictive models used by the stream

        Returns:
            proso.geography.model.PredictiveModel
        """
        return self._predictive_model


class PriorCurrentModel (PredictiveModel):

    """
    This model works with prior and current knowledge and both these components
    are estimated by their own models.
    """

    __metaclass__ = abc.ABCMeta

    def prepare(self, user_id, place_asked_id, options, question_type, inserted, environment):
        prior_status, prior_data = self.prior_prepare(
            user_id,
            place_asked_id,
            options,
            question_type,
            inserted,
            environment)
        current_status, current_data = self.current_prepare(
            user_id,
            place_asked_id,
            options,
            question_type,
            inserted,
            environment)
        current_predict = self.current_predict(
            user_id,
            place_asked_id,
            options,
            question_type,
            inserted,
            current_data)
        if prior_status == PHASE_SKIP:
            prior_predict = None
        else:
            prior_predict = self.prior_predict(
                user_id,
                place_asked_id,
                options,
                question_type,
                inserted,
                prior_data)
        return {
            'prior_status': prior_status,
            'prior_data': prior_data,
            'prior_predict': prior_predict,
            'current_status': current_status,
            'current_data': current_data,
            'current_predict': current_predict
        }

    def predict(self, user_id, place_asked_id, options, question_type, inserted, data):
        if data['prior_status'] == PHASE_PREDICT:
            return data['prior_predict']
        else:
            return data['current_predict']

    def update(self, answer, environment, data, prediction):
        if data['prior_status'] != PHASE_SKIP:
            self.prior_update(answer, environment, data['prior_data'], data['prior_predict'])
        if data['current_status'] != PHASE_SKIP:
            self.current_update(answer, environment, data['current_data'], data['current_predict'])

    @abc.abstractmethod
    def prior_prepare(self, user_id, place_asked_id, options, question_type, inserted, env):
        return

    @abc.abstractmethod
    def prior_predict(self, user_id, place_asked_id, options, question_type, inserted, data):
        return

    @abc.abstractmethod
    def prior_update(self, answer, environment, data, prediction):
        return

    @abc.abstractmethod
    def current_prepare(self, user_id, place_asked_id, options, question_type, inserted, env):
        return

    @abc.abstractmethod
    def current_predict(self, user_id, place_asked_id, options, question_type, inserted, data):
        return

    @abc.abstractmethod
    def current_update(self, answer, environment, data, prediction):
        return


class DefaultModel(PriorCurrentModel):

    def __init__(self, elo_alpha=1.0, elo_alpha_dynamic=0.05, pfae_good=3.4, pfae_bad=0.3, time_shift=80.0):
        self._elo_alpha = elo_alpha
        self._elo_alpha_dynamic = elo_alpha_dynamic
        self._pfae_good = pfae_good
        self._pfae_bad = pfae_bad
        self._time_shift = time_shift

    def prior_prepare(self, user_id, place_asked_id, options, question_type, inserted, env):
        return prior.elo_prepare(user_id, place_asked_id, options, question_type, inserted, env)

    def prior_predict(self, user_id, place_asked_id, options, question_type, inserted, data):
        return prior.elo_predict(user_id, place_asked_id, options, question_type, inserted, data)

    def prior_update(self, answer, environment, data, prediction):
        return prior.elo_update(answer, environment, data, prediction, alpha=self._elo_alpha, dynamic_alpha=self._elo_alpha_dynamic)

    def current_prepare(self, user_id, place_asked_id, options, question_type, inserted, env):
        return current.pfa_prepare(user_id, place_asked_id, options, question_type, inserted, env)

    def current_predict(self, user_id, place_asked_id, options, question_type, inserted, data):
        return current.pfa_predict(user_id, place_asked_id, options, question_type, inserted, data, time_shift=self._time_shift)

    def current_update(self, answer, environment, data, prediction):
        return current.pfa_update(answer, environment, data, prediction, k_good=self._pfae_good, k_bad=self._pfae_bad)


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
