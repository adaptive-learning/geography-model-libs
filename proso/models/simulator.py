# coding=utf-8
import abc
import random
import datetime
import prediction


class UserKnowledgeProvider:

    @abc.abstractmethod
    def prediction(self, user, item, options=None):
        pass

    @abc.abstractmethod
    def process_answer(user, item, correct, time, options=None):
        pass


class ConstantUserKnowledgeProvider(UserKnowledgeProvider):

    def __init__(self, users, items):
        self._skill= dict([(i, random.gauss(0.5, 0.1)) for i in users])
        self._difficulty = dict([(i, random.gauss(0.5, 1.5)) for i in items])

    def prediction(self, user, item, time, options=None):
        return prediction.predict_simple(self._skill - self._difficulty, len(options) if options else 0)

    def process_answer(user, item, correct, time, options=None):
        pass


class Activity:

    @abc.abstractmethod
    def next(self):
        pass


class OneUserActivitu(Activity):

    def __init__(self, user, time_start=datetime.datetime.now()):
        self._user = user
        self._time = time_start

    def next(self):
        self._time + datetime.timedelta(seconds=10)
        return self._user, self._time


class Generator:

    def answers(self, users, items, environment, predictive_model, recommendation, n):
        activity = self.activity(users)
        knowledge_provider = self.user_knowledge_provider(users, items)
        answers = []
        for i in range(n):
            user, time = activity.next()
            [r] = recommendation.recommend(environment, user, items, 1)
            item, options = r[0], r[1] if isinstance(r, tuple) else r[0], []
            prediction = predictive_model.predict(environment, user, item, time, options=options)
            if random.random() < knowledge_provider.prediction(user, item, options=options):
                correct = True
            else:
                correct = False
            knowledge_provider.process_answer(user, item, correct, time, options=options)
            predictive_model.predict_and_update(environment, user, item, correct, time)
            answered = item if correct else (random.choice(options) if options else None)
            environment.process_answer(user, item, item, answered, time)
            answers.append({
                'user': user,
                'time': time,
                'item': item,
                'options': options,
                'answered': answered
            })
        return answers

    @abc.abstractmethod
    def activity(self, user_ids):
        pass

    @abc.abstractmethod
    def user_knowledge_provider(self, user_ids, place_ids):
        pass