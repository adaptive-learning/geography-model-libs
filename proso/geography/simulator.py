import datetime
import random
import model
import recommendation


class UserKnowledgeProvider:

    def get_skill(self, user_id, place_id):
        raise NotImplementedError()

    def process_answer(user_id, place_asked_id, place_answered_id, inserted):
        raise NotImplementedError()


class SimpleUserKnowledgeProvider(UserKnowledgeProvider):

    def __init__(self, user_ids, place_ids):
        self._prior = dict([(i, random.gauss(0.5, 0.1)) for i in user_ids])
        self._difficulty = dict([(i, random.gauss(0.5, 1.5)) for i in place_ids])
        self._current = dict()

    def get_skill(self, user_id, place_id):
        return self._current.get(
            (user_id, place_id),
            self._prior[user_id] - self._difficulty[place_id])

    def process_answer(self, user_id, place_asked_id, place_answered_id, options, inserted):
        skill = self.get_skill(user_id, place_asked_id)
        correct = place_asked_id == place_answered_id
        asked_pred, options_pred = model.predict(
            skill,
            map(lambda i: self.get_skill(user_id, i), options))
        if correct:
            skill += 3.4 * (correct - asked_pred)
        else:
            skill += 0.3 * (correct - asked_pred)
        self._current[user_id, place_asked_id] = skill


class Activity:

    def next(self):
        raise NotImplementedError()


class SimpleActivity(Activity):

    def __init__(self, user_ids, concurrently=None):
        self._user_ids = user_ids
        self._last = dict([(i, datetime.datetime.now()) for i in user_ids])
        self._in_row = dict([(i, -1) for i in user_ids])
        if not concurrently:
            self._concurrently = int(max(1, min(100, round(len(user_ids) / 10.0))))
        else:
            self._concurrently = concurrently

    def next_activity(self):
        if all(map(lambda x: x == -1, self._in_row.values())):
            self._in_row = dict([(i, -1) for i in self._user_ids])
            self._last = dict(map(
                lambda (u, d): (u, d + datetime.timedelta(hours=24)),
                self._last.items()))
            concurrent = random.sample(self._user_ids, self._concurrently)
            for user_id in concurrent:
                self._in_row[user_id] = 0
        valid_users = [u for (u, x) in self._in_row.items() if x >= 0]
        candidate = random.choice(valid_users)
        if random.random() < 0.985 ** self._in_row[candidate]:
            self._in_row[candidate] += 1
        else:
            self._in_row[candidate] = -1
        self._last[candidate] += datetime.timedelta(seconds=1)
        return candidate, self._last[candidate]


class Generator:

    def answers(self, user_ids, place_ids, env, n):
        user_knowledge_provider = self.user_knowledge_provider(user_ids, place_ids)
        stream = self.stream(env)
        activity = self.activity(user_ids)
        answers = []
        for i in range(n):
            user_id, inserted = activity.next_activity()
            [(place_asked_id, options)] = self.recommend_question(user_id, place_ids, env, 1)
            asked_pred, options_pred = model.predict(
                user_knowledge_provider.get_skill(user_id, place_asked_id),
                map(lambda i: user_knowledge_provider.get_skill(user_id, i), options))
            r = random.random()
            if r < asked_pred:
                place_answered_id = place_asked_id
            elif len(options) == 0:
                place_answered_id = random.choice(place_ids)
            else:
                acc = asked_pred
                place_answered_id = None
                for o, p in zip(options, options_pred):
                    acc += p
                    if r < acc:
                        place_answered_id = o
            answer = {
                'place_asked': place_asked_id,
                'place_answered': place_answered_id,
                'user': user_id,
                'options': options,
                'inserted': inserted,
                'id': i
            }
            stream.stream_answer(answer)
            user_knowledge_provider.process_answer(
                user_id, place_asked_id, place_answered_id, options, inserted)
            answers.append(answer)
        return answers

    def activity(self, user_ids):
        raise NotImplementedError()

    def recommend_question(self, user_id, place_ids, env, n):
        raise NotImplementedError()

    def stream(self, env):
        raise NotImplementedError()

    def user_knowledge_provider(self, user_ids, place_ids):
        raise NotImplementedError()


class SimpleGenerator(Generator):

    def activity(self, user_ids):
        return SimpleActivity(user_ids)

    def recommend_question(self, user_id, place_ids, env, n):
        return recommendation.by_additive_function(user_id, place_ids, env, n)

    def stream(self, env):
        return model.DefaultAnswerStream(env)

    def user_knowledge_provider(self, user_ids, place_ids):
        return SimpleUserKnowledgeProvider(user_ids, place_ids)
