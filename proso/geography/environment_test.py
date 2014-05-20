#  -*- coding: utf-8 -*-

import unittest
import proso.geography.environment as environment


class InMemory(unittest.TestCase):

    def test_skills_and_difficulty(self):
        # setup
        env = environment.InMemoryEnvironment()
        # testing constants
        user_id = 1
        place_id = 2
        difficulty = 5
        prior_skill = 2
        current_skill = 10
        # tests for singles
        self.assertEqual(0, env.difficulty(place_id))
        self.assertEqual(0, env.prior_skill(user_id))
        self.assertEqual(0, env.current_skill(user_id, place_id))
        env.difficulty(place_id, difficulty)
        self.assertEqual(difficulty, env.difficulty(place_id))
        self.assertEqual(-difficulty, env.current_skill(user_id, place_id))
        env.prior_skill(user_id, prior_skill)
        self.assertEqual(prior_skill, env.prior_skill(user_id))
        self.assertEqual(prior_skill - difficulty, env.current_skill(user_id, place_id))
        env.current_skill(user_id, place_id, current_skill)
        self.assertEqual(current_skill, env.current_skill(user_id, place_id))
        self.assertEqual(-difficulty, env.current_skill(0, place_id))
        self.assertEqual(prior_skill, env.current_skill(user_id, 0))
        # tests for multiples
        self.assertEqual([difficulty, 0], env.difficulties([place_id, 0]))
        self.assertEqual([prior_skill, 0], env.prior_skills([user_id, 0]))
        self.assertEqual(
            [current_skill, prior_skill, -difficulty],
            env.current_skills([user_id, user_id, 0], [place_id, 0, place_id]))

    def test_first_answers_num(self):
        # setup
        env = environment.InMemoryEnvironment()
        # tests
        self.assertEqual(0, env.first_answers_num(user_id=1))
        self.assertEqual(0, env.first_answers_num(place_id=1))
        self.assertEqual(0, env.first_answers_num(1, 1))
        env.process_answer(1, 1, 1, None)
        env.process_answer(1, 1, 1, None)
        env.process_answer(1, 2, 2, None)
        env.process_answer(1, 3, 3, None)
        env.process_answer(2, 1, 1, None)
        self.assertEqual(3, env.first_answers_num(user_id=1))
        self.assertEqual(2, env.first_answers_num(place_id=1))
        self.assertEqual(1, env.first_answers_num(1, 1))

    def test_last_time(self):
        # setup
        env = environment.InMemoryEnvironment()
        # tests
        self.assertIsNone(env.last_time(user_id=1))
        self.assertIsNone(env.last_time(place_id=1))
        self.assertIsNone(env.last_time(1, 1))
        env.process_answer(1, 1, 1, 1)
        env.process_answer(1, 2, 2, 2)
        env.process_answer(2, 1, 1, 3)
        self.assertEqual(2, env.last_time(user_id=1))
        self.assertEqual(3, env.last_time(place_id=1))
        self.assertEqual(1, env.last_time(1, 1))
        self.assertEqual(
            [2, 3, None],
            env.last_times(user_ids=[1, 2, 0]))
        self.assertEqual(
            [3, 2, None],
            env.last_times(place_ids=[1, 2, 0]))
        self.assertEqual(
            [1, None],
            env.last_times(user_ids=[1, 1], place_ids=[1, 3]))

    def test_confused_index(self):
        # setup
        env = environment.InMemoryEnvironment()
        # tests
        self.assertEqual([0, 0], env.confused_index(1, [2, 3]))
        env.process_answer(1, 1, 2, 1)
        env.process_answer(1, 1, 1, 2)
        env.process_answer(1, 2, 1, 3)
        env.process_answer(1, 1, 3, 4)
        self.assertEqual([2, 1], env.confused_index(1, [2, 3]))

    def test_rolling_success(self):
        # setup
        env = environment.InMemoryEnvironment()
        # tests
        self.assertEqual(1.0, env.rolling_success(1))
        env.process_answer(1, 1, 2, 1)
        env.process_answer(1, 1, 1, 2)
        env.process_answer(1, 2, 1, 3)
        env.process_answer(1, 1, 3, 4)
        env.process_answer(2, 1, 2, 5)
        env.process_answer(2, 1, 1, 6)
        self.assertEqual(0.25, env.rolling_success(1))
        self.assertEqual(0.5, env.rolling_success(2))
