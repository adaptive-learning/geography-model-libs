# -*- coding: utf-8 -*-
import model

TIME_SHIFT = 80.0


def pfa_prepare(answer, env):
    all_place_ids = [answer['place_asked']] + answer['options']
    user_ids = [answer['user'] for i in all_place_ids]
    current_skills = env.current_skills(
        user_ids,
        all_place_ids)
    last_times = env.last_times(
        user_ids,
        all_place_ids)
    data = (current_skills, last_times)
    return (model.PHASE_PREDICT, data)


def pfa_predict(answer, data):
    current_skills, last_times = data
    seconds_ago = map(
        lambda x: (answer['inserted'] - x).total_seconds() if x is not None else 315360000,
        last_times)
    current_skills = map(
        lambda (skill, secs): skill + TIME_SHIFT / max(secs, 0.001),
        zip(current_skills, seconds_ago))
    if 'number_of_options' in answer and answer['number_of_options'] != len(answer['options']):
        # backward compatibility
        return model.predict_simple(current_skills[0], answer['number_of_options'])
    else:
        return model.predict(current_skills[0], current_skills[1:])
    return model.predict(current_skills[0], current_skills[1:0])


def pfa_update(answer, env, data, prediction):
    current_skills, last_times = data
    K_GOOD = 3.4
    K_BAD = 0.3
    result = answer['place_asked'] == answer['place_answered']
    if result:
        current_skill = current_skills[0] + K_GOOD * (result - prediction[0])
    else:
        current_skill = current_skills[0] + K_BAD * (result - prediction[0])
    env.current_skill(
        answer['user'],
        answer['place_asked'],
        current_skill)
