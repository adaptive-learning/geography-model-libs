# -*- coding: utf-8 -*-


class Environment:

    """
    This class encapsulates environment for the purpose of modelling.
    """

    def answers_num(self, user_id=None, place_id=None):
        raise NotImplementedError()

    def answers_nums(self, user_ids, place_ids):
        raise NotImplementedError()

    def confused_index(self, place_id, place_ids):
        raise NotImplementedError()

    def current_skill(self, user_id, place_id, new_value=None):
        raise NotImplementedError()

    def current_skills(self, user_id, place_ids):
        raise NotImplementedError()

    def difficulties(self, place_ids):
        raise NotImplementedError()

    def difficulty(self, place_id, new_value=None):
        raise NotImplementedError()

    def first_answers_num(self, user_id=None, place_id=None):
        raise NotImplementedError()

    def first_answers_nums(self, user_ids, place_ids):
        raise NotImplementedError()

    def flush(self):
        raise NotImplementedError()

    def has_answer(self, user_id=None, place_id=None):
        raise NotImplementedError()

    def have_answer(self, user_ids, place_ids):
        raise NotImplementedError()

    def prior_skill(self, user_id, new_value=None):
        raise NotImplementedError()

    def process_answer(self, user_id, place_asked_id, place_answered_id, time):
        raise NotImplementedError()

    def last_time(self, user_id=None, place_id=None):
        raise NotImplementedError()

    def last_times(self, user_ids, place_ids):
        raise NotImplementedError()

    def rolling_success(self, user_id):
        raise NotImplementedError()


class InMemoryEnvironment(Environment):

    _EMPTY_RECORD = {
        'first_answers_num': 0,
        'answers_num': 0,
        'last_time': None,
        'last_ten_answers': [],
    }

    def __init__(self):
        self._current_skill = {}
        self._difficulty = {}
        self._prior_skill = {}
        self._records = {}
        self._confused_index = dict()

    def with_difficulty(self, difficulty):
        self._difficulty = difficulty

    def export_difficulty(self):
        return self._difficulty

    def export_prior_skill(self):
        return self._prior_skill

    def answers_num(self, user_id=None, place_id=None):
        return self._record(user_id=user_id, place_id=place_id)['answers_num']

    def answers_nums(self, user_ids, place_ids):
        return map(
            lambda (user_id, place_id): self.answers_num(user_id, place_id),
            zip(user_ids, place_ids))

    def confused_index(self, place_id, place_ids):
        make_key = lambda i: self._make_confused_index_key(place_id, i)
        return map(
            lambda key: self._confused_index.get(key, 0),
            map(make_key, place_ids))

    def current_skill(self, user_id, place_id, new_value=None):
        if new_value is not None:
            self._current_skill[user_id, place_id] = new_value
        else:
            return self._current_skill.get(
                (user_id, place_id),
                self.prior_skill(user_id) - self.difficulty(place_id))

    def current_skills(self, user_ids, place_ids):
        return map(
            lambda (user_id, place_id): self.current_skill(user_id, place_id),
            zip(user_ids, place_ids))

    def difficulty(self, place_id, new_value=None):
        if new_value is not None:
            self._difficulty[place_id] = new_value
        else:
            return self._difficulty.get(place_id, 0)

    def difficulties(self, place_ids):
        return map(self.difficulty, place_ids)

    def first_answers_num(self, user_id=None, place_id=None):
        return self._record(user_id=user_id, place_id=place_id)['first_answers_num']

    def first_answers_nums(self, user_ids, place_ids):
        return map(
            lambda (user_id, place_id): self.first_answers_num(user_id, place_id),
            zip(user_ids, place_ids))

    def flush(self):
        return self.flush_all(self._prior_skill, self._current_skill, self._difficulty)

    def flush_all(self, prior_skill, current_skill, difficulty):
        pass

    def has_answer(self, user_id=None, place_id=None):
        return self.first_answers_num(user_id=user_id, place_id=place_id) > 0

    def have_answer(self, user_ids=None, place_ids=None):
        return map(
            lambda (user_id, place_id): self.has_answer(user_id, place_id),
            zip(user_ids, place_ids))

    def prior_skill(self, user_id, new_value=None):
        if new_value is not None:
            self._prior_skill[user_id] = new_value
        else:
            return self._prior_skill.get(user_id, 0)

    def prior_skills(self, user_ids):
        return map(self.prior_skill, user_ids)

    def process_answer(self, user_id, place_asked_id, place_answered_id, time):
        is_first = not self.has_answer(user_id=user_id, place_id=place_asked_id)
        update_num = 1 if is_first else 0
        record_both = self._record(user_id=user_id, place_id=place_asked_id)
        self._record(
            user_id=user_id,
            place_id=place_asked_id,
            last_time=time,
            first_answers_num=record_both['first_answers_num'] + update_num,
            answers_num=record_both['answers_num'] + 1)
        record_user = self._record(user_id=user_id)
        last_ten_answers = record_user['last_ten_answers']
        if len(last_ten_answers) == 0:
            last_ten_answers = list(last_ten_answers)  # copy
        if len(last_ten_answers) == 10:
            last_ten_answers = last_ten_answers[1:10]
        last_ten_answers.append(place_asked_id == place_answered_id)
        self._record(
            user_id=user_id,
            last_time=time,
            first_answers_num=record_user['first_answers_num'] + update_num,
            last_ten_answers=last_ten_answers,
            answers_num=record_user['answers_num'] + 1)
        record_place = self._record(place_id=place_asked_id)
        self._record(
            place_id=place_asked_id,
            last_time=time,
            first_answers_num=record_place['first_answers_num'] + update_num,
            answers_num=record_place['answers_num'] + 1)
        if place_asked_id != place_answered_id:
            confused_index_key = self._make_confused_index_key(place_asked_id, place_answered_id)
            old = self._confused_index.get(confused_index_key, 0)
            self._confused_index[confused_index_key] = old + 1

    def last_time(self, user_id=None, place_id=None):
        return self._record(user_id=user_id, place_id=place_id)['last_time']

    def last_times(self, user_ids=None, place_ids=None):
        if not user_ids and not place_ids:
            raise Exception('Either user_id or place_id have to be given.')
        if user_ids and place_ids:
            return map(
                lambda (user_id, place_id): self.last_time(user_id, place_id),
                zip(user_ids, place_ids))
        if user_ids:
            return map(self.last_time, user_ids)
        return map(lambda place_id: self.last_time(place_id=place_id), place_ids)

    def rolling_success(self, user_id):
        last_ten_answers = self._record(user_id=user_id).get('last_ten_answers')
        if len(last_ten_answers) == 0:
            return 1.0
        else:
            return float(sum(last_ten_answers)) / len(last_ten_answers)

    def _make_confused_index_key(self, i, j):
        return (i, j) if i < j else (j, i)

    def _record(self, user_id=None, place_id=None, **kwargs):
        key = self._record_key(user_id=user_id, place_id=place_id)
        if len(kwargs):
            if key in self._records:
                record = self._records[key]
            else:
                record = InMemoryEnvironment._EMPTY_RECORD.copy()
            for k, v in kwargs.iteritems():
                record[k] = v
            self._records[key] = record
        else:
            return self._records.get(key, InMemoryEnvironment._EMPTY_RECORD.copy())

    def _record_key(self, user_id=None, place_id=None):
        if user_id is None and place_id is None:
            raise Exception('Either user_id or place_id have to be given.')
        if user_id is not None and place_id is not None:
            return ('user_place', (user_id, place_id))
        if user_id is not None:
            return ('user', user_id)
        return ('place', place_id)
