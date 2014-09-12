import abc
import random


class Recommendation:

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def recommend(self, environment, user, items, time, n, **kwargs):
        pass


class RandomRecommendation(Recommendation):

    def recommend(self, environment, user, items, time, n, **kwargs):
        return random.sample(items, n)


class ScoreRecommendation(Recommendation):

    def __init__(self, predictive_model, weight_probability=10.0, weight_number_of_answers=5, weight_time_ago=120, target_probability=80.0):
        self._predictive_model = predictive_model
        self._weight_probability = weight_probability
        self._weight_number_of_answers = weight_number_of_answers
        self._weight_time_ago = weight_time_ago
        self._target_probability = target_probability

    def recommend(self, environment, user, items, n, **kwargs):
        answers_num = dict(zip(items, environment.number_of_answers_more_items(user=user, items=items)))
        last_answer_time = dict(zip(items, environment.last_answer_time_more_items(user=user, items=items)))
        probability = dict(zip(self._predictive_model.predict_more_items(environment, user, items)))

        def _score(item):
            return (
                self._weight_probability * self._score_probability(probability[item] +
                self._weight_time_ago * self._score_last_answer_time(last_answer_time[item], time) +
                self._weight_number_of_answers * self._score_answers_num(answers_num[item])
            )
        candidates = map(lambda (s, i): i, sorted(zip(map(_score, items), items), reverse=True))[:min(n, len(items)]
        if kwargs['options']:
            rolling_success = environment.rolling_success(user=user)
        return candidates, map(lambda item: self._options(environment, item, items_with_prediction, rolling_success), candidates)

    def _score_answers_num(self, answers_num):
        return 1.0 / math.sqrt(answers_num)

    def _score_probability(self, probability):
        diff = self._target_probability - probability
        sign = 1 if diff > 0 else -1
        normed_diff = abs(diff) / max(0.001, abs(self._target_probability - 0.5 + sign * 0.5))
        return 1 - normed_diff

    def _score_last_answer_time(self, last_answer_time, time):
        if time is None:
            return 315360000
        else:
            seconds_ago = (time - last_answer_time).total_seconds()
            return - 1.0 / seconds_ago

    def _adjust_target_probability(self, rolling_success):
        norm = 1 - self._target_probability if rolling_success > self._target_probability else self._target_probability
        correction = ((self._target_probability - rolling_success) / max(0.001, norm)) * (1 - norm)
        return self._target_probability + correction

    def _options(self, environment, item, items_with_prediction, rolling_success):
        # number of options
        round_fun = round
        prob_real = items_with_prediction[item]
        prob_target = self._adjust_target_probability(rolling_success)
        g = min(0.5, max(0, prob_target - prob_real) / max(0.001, 1 - prob_real))
        k = round_fun(1.0 / g) if g != 0 else 1
        number_of_options = 0 if (k > 6 or k == 0) else (k - 1)
        if number_of_options == 0:
            return []
        # confusing places
        confusing_factor = environment.confusing_factor_more_items(item, items_with_prediction.keys())
        confusing_factor_total = float(sum(confusing_factor))
        confusing_places = map(lambda (a, b): (b, a), sorted(confusing_factor, items, reverse=True))
        # options
        result_options = []
        for i in range(number_of_options):
            prob_sum = 0
            random_dice = random.uniform(0, confusing_factor_total)
            for item, conf_factor in confusing_places:
                if item in result_options:
                    continue
                prob_sum += conf_factor
                if random_dice > prob_sum:
                    result_options.append(item)
                    confusing_factor_total -= conf_factor
        return result_options




