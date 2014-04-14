#  -*- coding: utf-8 -*-

import unittest
import proso.geography.model as model


class TestBasics(unittest.TestCase):

    def test_predict(self):
        sum_probs = lambda x, xs: x + sum(xs)
        asked_prob, [opt_prob] = model.predict(-100, [100])
        self.assertAlmostEqual(1.0, asked_prob)
        self.assertAlmostEqual(0.0, opt_prob)
        for i in range(1, 10):
            asked_prob, opt_probs = model.predict(0, [0 for j in range(i)])
            self.assertAlmostEqual(1.0, sum_probs(asked_prob, opt_probs))
            self.assertGreater(asked_prob, 1.0 / (i + 1) + (1 - (1.0 / (i + 1))) * 0.5)
