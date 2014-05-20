import numpy.random as random
import model
import math
import datetime


TARGET_PROBABILITY = 0.8


def by_random(user_id, place_ids, env, n):
    targets = random.choice(place_ids, size=n)
    confused_indexes = map(lambda target: env.confused_index(target, place_ids), targets)
    user_ids = [user_id for i in targets]
    have_answer = env.have_answer(user_ids=user_ids, place_ids=targets)
    target_prob = adjust_target_probability(
        TARGET_PROBABILITY,
        env.rolling_success(user_id))
    estimated = zip(*map(
        lambda skill: model.predict_simple(skill, 0),
        env.current_skills(user_ids=user_ids, place_ids=targets)))[0]
    return zip(targets, map(
        lambda (t, e, h, c): _options(place_ids, t, target_prob, e, h, c),
        zip(targets, estimated, have_answer, confused_indexes)))


def by_additive_function(user_id, place_ids, env, n):
    WEIGHT_PROBABILITY = 10
    WEIGHT_NUMBER_OF_ANSWERS = 5
    WEIGHT_TIME_AGO = 120

    user_ids = [user_id for i in place_ids]
    target_prob = adjust_target_probability(
        TARGET_PROBABILITY,
        env.rolling_success(user_id))
    seconds_ago = map(
        lambda x: (datetime.datetime.now() - x).total_seconds() if x is not None else 315360000,
        env.last_times(user_ids=user_ids, place_ids=place_ids))
    nums_of_ans = env.answers_nums(user_ids=user_ids, place_ids=place_ids)
    estimated = zip(*map(
        lambda skill: model.predict_simple(skill, 0),
        env.current_skills(user_ids=user_ids, place_ids=place_ids)))[0]
    estimated_dict = dict(zip(place_ids, estimated))
    score_time = map(_by_additive_time_ago, seconds_ago)
    score_num = map(_by_additive_number_of_answers, nums_of_ans)
    score_prob = map(lambda x: _by_additive_prob_diff(target_prob, x), estimated)
    score_total = map(
        lambda (x, y, z): WEIGHT_TIME_AGO * x + WEIGHT_NUMBER_OF_ANSWERS * y + WEIGHT_PROBABILITY * z,
        zip(score_time, score_num, score_prob))
    targets = zip(*sorted(zip(score_total, place_ids), reverse=True))[1][:min(n, len(place_ids))]
    targets_estimated = map(lambda i: estimated_dict[i], targets)
    t_user_ids = [user_id for i in targets]
    confused_indexes = map(lambda target: env.confused_index(target, place_ids), targets)
    have_answer = env.have_answer(user_ids=t_user_ids, place_ids=targets)
    return zip(targets, map(
        lambda (t, e, h, c): _options(place_ids, t, target_prob, e, h, c),
        zip(targets, targets_estimated, have_answer, confused_indexes)))


def _by_additive_time_ago(seconds_ago):
    return - 1.0 / max(seconds_ago, 1)


def _by_additive_number_of_answers(n):
    return 1.0 / math.sqrt(n + 1)


def _by_additive_prob_diff(expected, given):
    diff = expected - given
    sign = 1 if diff > 0 else -1
    normed_diff = abs(diff) / abs(expected - 0.5 + sign * 0.5)
    return 1 - normed_diff


def _options(place_ids, question_target, target_prob, estimated_prob, has_answer, confused_indexes):
    num_of_options = _number_of_options(target_prob, estimated_prob, has_answer)
    conf_places = zip(confused_indexes, place_ids)
    conf_places.sort()
    conf_places = map(lambda (a, b): (b, a), conf_places)
    choices, weights = zip(*conf_places)
    return _weighted_choices(choices, weights, num_of_options)


def _number_of_options(prob_target, prob_real, has_answer):
    round_fun = round if has_answer else math.floor
    g = min(0.5, max(0, prob_target - prob_real) / (1 - prob_real))
    k = round_fun(1.0 / g) if g != 0 else 1
    return 1 if k > 6 else k


def adjust_target_probability(target, rolling_success):
    norm = 1 - target if rolling_success > target else target
    correction = ((target - rolling_success) / norm) * (1 - norm)
    return target + correction


def _weighted_choices(choices, weights, n):
    if sum(weights) == 0:
        return random.choice(choices)
    if n >= len(choices):
        return choices
    chosen = []
    choices_set = set(zip(choices, weights))
    for i in range(int(n)):
        c, w = _weighted_choice(choices_set)
        chosen.append(c)
        choices_set.remove((c, w))
    return chosen


def _weighted_choice(choices_with_weights):
    if not len(choices_with_weights):
        raise Exception("The list 'choices' can't be empty.")
    upto = 0
    total = sum(zip(*choices_with_weights)[1])
    r = random.uniform(0, total)
    for c, w in choices_with_weights:
        if upto + w > r:
            return c, w
        upto += w
    assert False, "Shouldn't get here"
