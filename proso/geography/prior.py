# -*- coding: utf-8 -*-
import model


def elo_prepare(user_id, place_asked_id, options, question_type, inserted, environment):
    all_place_ids = options if options else [place_asked_id]
    user_ids = [user_id for i in all_place_ids]
    [is_not_first] = environment.have_answer(
        [user_id],
        [place_asked_id])
    if is_not_first:
        return (model.PHASE_SKIP, None)
    place_first_answers_nums = environment.first_answers_nums(
        [None for i in all_place_ids],
        place_ids=all_place_ids
    )
    user_first_answers_num = environment.first_answers_num(user_id)
    difficulties = environment.difficulties(all_place_ids)
    prior_skill = environment.prior_skill(user_id)
    current_skills = environment.current_skills(
        user_ids,
        all_place_ids)
    data = (current_skills, difficulties, place_first_answers_nums, prior_skill, user_first_answers_num)
    return (model.PHASE_PREDICT, data)


def elo_predict(user_id, place_asked_id, options, question_type, inserted, data):
    current_skills, difficulties, place_first_answers_nums, prior_skill, user_first_answers_num = data
    return model.predict(current_skills[0], current_skills[1:])


def elo_update(answer, environment, data, prediction, alpha=1.0, dynamic_alpha=0.05):
    current_skills, difficulties, place_first_answers_nums, prior_skill, user_first_answers_num = data
    alpha_fun = lambda n: alpha / (1 + dynamic_alpha * n)
    prior_skill_alpha = alpha_fun(user_first_answers_num)
    difficulty_alpha = alpha_fun(place_first_answers_nums[0])
    result = answer['place_asked'] == answer['place_answered']
    environment.prior_skill(
        answer['user'],
        prior_skill + prior_skill_alpha * (result - prediction[0]))
    environment.difficulty(
        answer['place_asked'],
        difficulties[0] - difficulty_alpha * (result - prediction[0]))
