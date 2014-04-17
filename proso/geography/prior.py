# -*- coding: utf-8 -*-
from model import predict, PHASE_SKIP, PHASE_PREDICT, PHASE_UPDATE


def elo_prepare(answer, env):
    all_place_ids = [answer['place_asked_id']] + answer['options']
    user_ids = [answer['user_id'] for i in all_place_ids]
    is_not_first = env.have_answer(
        user_ids,
        all_place_ids)
    is_first = [not i for i in is_not_first]
    if all(is_not_first):
        return (PHASE_SKIP, None)
    place_first_answers_nums = env.first_answers_nums(
        [None for i in all_place_ids],
        place_ids=all_place_ids
    )
    user_first_answers_num = env.first_answers_num(answer['user_id'])
    difficulties = env.difficulties(all_place_ids)
    prior_skill = env.prior_skill(answer['user_id'])
    current_skills = env.current_skills(
        user_ids,
        all_place_ids)
    data = (current_skills, difficulties, place_first_answers_nums, prior_skill, user_first_answers_num)
    if is_first[0]:
        return (PHASE_PREDICT, data)
    return (PHASE_UPDATE, data)


def elo_predict(answer, data):
    current_skills, difficulties, place_first_answers_nums, prior_skill, user_first_answers_num = data
    return predict(current_skills[0], current_skills[1:])


def elo_update(answer, env, data, prediction):
    current_skills, difficulties, place_first_answers_nums, prior_skill, user_first_answers_num = data
    ALPHA = 1.0
    DYNAMIC_ALPHA = 0.05
    alpha_fun = lambda n: ALPHA / (1 + DYNAMIC_ALPHA * n)
    prior_skill_alpha = alpha_fun(place_first_answers_nums[0])
    difficulty_alpha = alpha_fun(user_first_answers_num)
    result = answer['place_asked_id'] == answer['place_answered_id']
    env.prior_skill(
        answer['user_id'],
        prior_skill + prior_skill_alpha * (result - prediction[0]))
    env.difficulty(
        answer['place_asked_id'],
        difficulties[0] - difficulty_alpha * (result - prediction[0]))
