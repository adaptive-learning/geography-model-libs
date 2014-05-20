#  -*- coding: utf-8 -*-

import unittest
import prior
import current
import proso.geography.environment as environment
import model
import datetime
import recommendation


class TestAnswerStream(model.AnswerStream):

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


class AbstractTest(unittest.TestCase):

    def recommend_fun(self):
        return None

    def test_common_usage(self):
        # setup
        recommend_fun = self.recommend_fun()
        if recommend_fun is None:
            return
        env = environment.InMemoryEnvironment()
        stream = TestAnswerStream(env)
        self.prepare_stream(stream)

        # test
        recommended = recommend_fun(0, range(100), env, 10)
        for target, options in recommended:
            skill = env.current_skill(0, target)
            prediction_alone = model.predict_simple(skill, 0)[0]
            if prediction_alone < 0.5:
                self.assertEqual(len(options), 2)
            elif prediction_alone > 0.9:
                self.assertEqual(len(options), 0)
            else:
                self.assertGreater(len(options), 1)
                self.assertLess(len(options), 7)

    def prepare_stream(self, stream):
        user_ids = range(100)
        place_ids = range(100)
        for user_id in user_ids:
            for place_id in place_ids:
                stream.stream_answer({
                    'user': user_id,
                    'place_asked': place_id,
                    'place_answered': place_id + ((user_id + place_id) % 6),
                    'inserted': datetime.datetime.now() - datetime.timedelta(hours=12),
                    'options': []
                })


class RandomTest(AbstractTest):

    def recommend_fun(self):
        return recommendation.by_random


class AdditiveTest(AbstractTest):

    def recommend_fun(self):
        return recommendation.by_additive_function

    def test_repetition(self):
        # setup
        recommend_fun = self.recommend_fun()
        env = environment.InMemoryEnvironment()
        stream = TestAnswerStream(env)
        self.prepare_stream(stream)

        # test
        recommended_before = recommend_fun(0, range(100), env, 10)
        to_answer = recommended_before[0]
        stream.stream_answer({
            'user': 0,
            'place_asked': to_answer[0],
            'place_answered': to_answer[0],
            'inserted': datetime.datetime.now(),
            'options': to_answer[1]
        })
        recommend_after = recommend_fun(0, range(100), env, 10)
        self.assertNotEqual(recommend_after[0][0], recommended_before[0][0])
