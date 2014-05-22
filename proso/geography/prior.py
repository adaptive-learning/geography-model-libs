# -*- coding: utf-8 -*-
import model


def elo_prepare(answer, env):
    all_place_ids = [answer['place_asked']] + answer['options']
    user_ids = [answer['user'] for i in all_place_ids]
    [is_not_first] = env.have_answer(
        [answer['user']],
        [answer['place_asked']])
    if is_not_first:
        return (model.PHASE_SKIP, None)
    place_first_answers_nums = env.first_answers_nums(
        [None for i in all_place_ids],
        place_ids=all_place_ids
    )
    user_first_answers_num = env.first_answers_num(answer['user'])
    difficulties = env.difficulties(all_place_ids)
    prior_skill = env.prior_skill(answer['user'])
    current_skills = env.current_skills(
        user_ids,
        all_place_ids)
    data = (current_skills, difficulties, place_first_answers_nums, prior_skill, user_first_answers_num)
    return (model.PHASE_PREDICT, data)


def elo_predict(answer, data):
    current_skills, difficulties, place_first_answers_nums, prior_skill, user_first_answers_num = data
    if 'number_of_options' in answer and answer['number_of_options'] != len(answer['options']):
        # backward compatibility
        return model.predict_simple(current_skills[0], answer['number_of_options'])
    else:
        return model.predict(current_skills[0], current_skills[1:])


def elo_update(answer, env, data, prediction):
    current_skills, difficulties, place_first_answers_nums, prior_skill, user_first_answers_num = data
    ALPHA = 1.0
    DYNAMIC_ALPHA = 0.05
    alpha_fun = lambda n: ALPHA / (1 + DYNAMIC_ALPHA * n)
    prior_skill_alpha = alpha_fun(user_first_answers_num)
    difficulty_alpha = alpha_fun(place_first_answers_nums[0])
    result = answer['place_asked'] == answer['place_answered']
    env.prior_skill(
        answer['user'],
        prior_skill + prior_skill_alpha * (result - prediction[0]))
    env.difficulty(
        answer['place_asked'],
        difficulties[0] - difficulty_alpha * (result - prediction[0]))
