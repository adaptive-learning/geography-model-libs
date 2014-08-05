# -*- coding: utf-8 -*-
import model


DEFAULT_TIME_SHIFT = 80.0


def pfa_prepare(user_id, place_asked_id, options, question_type, inserted, environment):
    all_place_ids = options if options else [place_asked_id]
    user_ids = [user_id for i in all_place_ids]
    current_skills = environment.current_skills(
        user_ids,
        all_place_ids)
    last_times = environment.last_times(
        user_ids,
        all_place_ids)
    data = (current_skills, last_times)
    return (model.PHASE_PREDICT, data)


def pfa_predict(user_id, place_asked_id, options, question_type, inserted, data, time_shift=DEFAULT_TIME_SHIFT):
    current_skills, last_times = data
    seconds_ago = map(
        lambda x: (inserted - x).total_seconds() if x is not None else 315360000,
        last_times)
    current_skills = map(
        lambda (skill, secs): skill + time_shift / max(secs, 0.001),
        zip(current_skills, seconds_ago))
    return model.predict(current_skills[0], current_skills[1:])


def pfa_update(answer, environment, data, prediction, k_good=3.4, k_bad=0.3):
    current_skills, last_times = data
    result = answer['place_asked'] == answer['place_answered']
    if result:
        current_skill = current_skills[0] + k_good * (result - prediction[0])
    else:
        current_skill = current_skills[0] + k_bad * (result - prediction[0])
    environment.current_skill(
        answer['user'],
        answer['place_asked'],
        current_skill)
