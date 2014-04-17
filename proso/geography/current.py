# -*- coding: utf-8 -*-
from model import predict, PHASE_PREDICT


def pfa_prepare(answer, env):
    all_place_ids = [answer['place_asked_id']] + answer['options']
    user_ids = [answer['user_id'] for i in all_place_ids]
    current_skills = env.current_skills(
        user_ids,
        all_place_ids)
    last_times = env.last_times(
        user_ids,
        all_place_ids)
    data = (current_skills, last_times)
    return (PHASE_PREDICT, data)


def pfa_predict(answer, data):
    current_skills, last_times = data
    return predict(current_skills[0], current_skills[1:0])


def pfa_update(answer, env, data, prediction):
    current_skills, last_times = data
    K_GOOD = 3.4
    K_BAD = 0.3
    result = answer['place_asked_id'] == answer['place_answered_id']
    if result:
        current_skill = current_skills[0] + K_GOOD * (result - prediction[0])
    else:
        current_skill = current_skills[0] + K_BAD * (result - prediction[0])
    env.current_skill(
        answer['user_id'],
        answer['place_asked_id'],
        current_skill)
