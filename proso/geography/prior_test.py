#  -*- coding: utf-8 -*-

import proso.geography.environment as environment
import proso.geography.model as model
import proso.geography.prior as prior
import unittest
import datetime


class TestBasics(unittest.TestCase):

    def test_elo(self):
        env = environment.InMemoryEnvironment()

        self.answers_for_place(env, 1, 2, range(1, 20), [])
        answer = {
            'user': 100000,
            'place_asked': 1,
            'place_answered': 2,
            'options': [],
            'question_type': 1,
            'inserted': datetime.datetime.now()
        }
        status, data = prior.elo_prepare(
            answer['user'],
            answer['place_asked'],
            answer['options'],
            answer['question_type'],
            answer['inserted'], env)
        prediction = prior.elo_predict(
            answer['user'],
            answer['place_asked'],
            answer['options'],
            answer['question_type'],
            answer['inserted'], data)
        self.assertGreater(0.1, prediction[0])

        self.answers_for_place(env, 1, 1, range(21, 40), [])
        answer = {
            'user': 100000,
            'place_asked': 1,
            'place_answered': 2,
            'options': [],
            'question_type': 1,
            'inserted': datetime.datetime.now()
        }
        status, data = prior.elo_prepare(
            answer['user'],
            answer['place_asked'],
            answer['options'],
            answer['question_type'],
            answer['inserted'], env)
        prediction = prior.elo_predict(
            answer['user'],
            answer['place_asked'],
            answer['options'],
            answer['question_type'],
            answer['inserted'], data)
        self.assertGreater(1, prediction[0])
        self.assertLess(0.5, prediction[0])

    def answers_for_place(self, env, place_asked_id, place_answered_id, users, options):
        for user_id in users:
            answer = {
                'user': user_id,
                'place_asked': place_asked_id,
                'place_answered': place_answered_id,
                'options': options,
                'question_type': 1,
                'inserted': datetime.datetime.now()
            }
            status, data = prior.elo_prepare(
                answer['user'],
                answer['place_asked'],
                answer['options'],
                answer['question_type'],
                answer['inserted'], env)
            self.assertEqual(model.PHASE_PREDICT, status)
            prediction = prior.elo_predict(
                answer['user'],
                answer['place_asked'],
                answer['options'],
                answer['question_type'],
                answer['inserted'], data)
            prior.elo_update(answer, env, data, prediction)

    def answers_for_user(self, env, user_id, to_ask, to_answer, options):
        for place_asked_id, place_answered_id in zip(to_ask, to_answer):
            answer = {
                'user': user_id,
                'place_asked': place_asked_id,
                'place_answered': place_answered_id,
                'options': options,
                'question_type': 1,
                'inserted': datetime.datetime.now()
            }
            status, data = prior.elo_prepare(
                answer['user'],
                answer['place_asked'],
                answer['options'],
                answer['question_type'],
                answer['inserted'], env)
            self.assertEqual(model.PHASE_PREDICT, status)
            prediction = prior.elo_predict(
                answer['user'],
                answer['place_asked'],
                answer['options'],
                answer['question_type'],
                answer['inserted'], data)
            prior.elo_update(answer, env, data, prediction)
