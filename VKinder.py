# -*- coding: utf-8 -*-
from random import randrange
import datetime as dt
from pprint import pprint
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from VKinder_bd import *


def get_vk_bot_token():
    with open('client_secret.txt', 'r') as token_file:
        return token_file.readline().strip()


def get_vk_user_token():
    with open('user_tokenVK.txt', 'r') as token_file:
        return token_file.readline().strip()


vk_bot = vk_api.VkApi(token=get_vk_bot_token())
vk_user = vk_api.VkApi(token=get_vk_user_token())
longpoll = VkBotLongPoll(vk_bot, '218792365')


def write_msg(user_id, message, attachment=' '):
    try:
        vk_bot.method('messages.send', {'user_id': user_id,
                                        'message': message,
                                        'random_id': randrange(10 ** 7),
                                        'attachment': attachment})
    except vk_api.exceptions.ApiError as err:
        print(err)


def get_user_info(user_id):
    resp = vk_bot.method('users.get', {'user_id': user_id, 'v': 5.131, 'fields': 'bdate, city, sex, domain'})
    return resp[0]


def get_message(user_id):
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.obj['message']['from_id'] == user_id:
                return event.obj['message']['text']


def get_age(user_id, user_info):
    if 'bdate' not in user_info:
        write_msg(user_id, 'Введите Ваш возраст')
        age = get_message(user_id)
        while len(age) < 2 or len(age) >= 3 or not age.isdigit():
            write_msg(user_id, 'Введите 2 цифры Вашего возраста!')
            age = get_message(user_id)
        return int(age)
    now = dt.datetime.now().replace(second=0, microsecond=0)
    date = user_info['bdate']
    if len(date) > 4:
        birthday = dt.datetime.strptime(date, '%d.%m.%Y')
    else:
        write_msg(user_id, 'Введите Ваш год рождения')
        year = get_message(user_id)
        while not year.isdigit() or len(year) != 4:
            write_msg(user_id, 'Введите 4 цифры Вашего года рождения!')
            year = get_message(user_id)
        birthday = dt.datetime.strptime(f'{date}.{year}', '%d.%m.%Y')
    age = (now - birthday).days // 365
    return age


def get_city(user_id, user_info):
    if 'city' not in user_info:
        write_msg(user_id, 'Введите Ваш город\nМожно по английски')
        city = get_message(user_id)
        while not city.isalpha():
            write_msg(user_id, 'Введите название города!')
            city = get_message(user_id)
        city_id = check_city(city)
        while not city_id:
            write_msg(user_id, 'Нет такого города, введите правильное название Вашего города!')
            city = get_message(user_id)
            city_id = check_city(city)
        return city_id[0]
    return user_info['city']


def check_city(city):
    fields = {
        'country_id': 1,
        'q': city,
        'count': 1
    }
    response = vk_user.method('database.getCities', values=fields)
    return response['items']


def get_person_id(user_info, city, age):
    fields = {
        'count': 1000,
        'v': 5.131,
        'city': city,
        'sex': 3 - user_info['sex'],
        'status': 6,
        'age_from': age - 2,
        'age_to': age + 10,
        'has_photo': 1
    }
    response = vk_user.method('users.search', values=fields)
    open_page_persons_id = []
    for person in response.get('items'):
        if not person['is_closed']:
            open_page_persons_id.append(person['id'])
    for person_id in open_page_persons_id:
        yield person_id


def get_photos(person_id):
    params = {
        'owner_id': person_id,
        'album_id': 'profile',
        'extended': 1,
        'v': 5.131
    }
    response = vk_user.method('photos.get', values=params)
    if response['count'] < 3:
        return False
    else:
        best_photos = sorted(response['items'],
                             key=lambda x: x['likes']['count'] + x['comments']['count'], reverse=True)[:3]
        photos_data = []
        for p in best_photos:
            photo_data = f"photo{p['owner_id']}_{p['id']}"
            photos_data.append(photo_data)
        return photos_data


def send_photos(user_id, person_id, photos_data):
    person_info = get_user_info(person_id)
    send_person_info = f"{person_info['first_name']} {person_info['last_name']}\nhttps://vk.com/{person_info['domain']}"
    write_msg(user_id, send_person_info)
    for _ in range(3):
        write_msg(user_id, f'Фото {_ + 1}', photos_data[_])


def main(user_id):
    create_tables()
    info = get_user_info(user_id)
    age = get_age(user_id, info)
    if age < 18:
        return write_msg(user_id, 'Минимальный возраст 18 лет')
    city = get_city(user_id, info)
    download_user_data(user_id, info['first_name'], info['last_name'], age, city['title'])
    while True:
        try:
            for person_id in get_person_id(info, city['id'], age):
                if not check_person_data(user_id, person_id):
                    pprint(get_user_info(person_id))
                    photos_data = get_photos(person_id)
                    if photos_data:
                        send_photos(user_id, person_id, photos_data)
                        download_person_data(user_id, person_id, get_user_info(person_id)['first_name'],
                                             get_user_info(person_id)['last_name'])
                        write_msg(user_id, 'Искать еще?\nЕсли устали, напишите "нет" или "no"')
                        continue_ = get_message(user_id).lower()
                        if continue_ == 'нет' or continue_ == 'no' or continue_ == 'n' or continue_ == 'н':
                            return write_msg(user_id, 'До свидания')
        except StopIteration:
            continue


while True:
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            message = event.obj['message']
            user_id = message['from_id']
            write_msg(user_id, 'Здравствуйте! Хотите найти пару, напишите "да" или "yes"?')
            answer = get_message(user_id).lower()
            if 'да' in answer or 'yes' in answer or 'д' in answer or 'y' in answer:
                main(user_id)
            else:
                write_msg(user_id, 'До свидания')
                continue
