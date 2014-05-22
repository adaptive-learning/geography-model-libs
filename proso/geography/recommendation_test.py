#  -*- coding: utf-8 -*-

import unittest
import proso.geography.environment as environment
import model
import datetime
import recommendation


class AbstractTest(unittest.TestCase):

    def recommend_fun(self):
        return None

    def test_common_usage(self):
        # setup
        recommend_fun = self.recommend_fun()
        if recommend_fun is None:
            return
        env = environment.InMemoryEnvironment()
        stream = model.DefaultAnswerStream(env)
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
        stream = model.DefaultAnswerStream(env)
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
