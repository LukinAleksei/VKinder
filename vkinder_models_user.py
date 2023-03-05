# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
import vk_api


load_dotenv()

vk_user_token = os.getenv('VK_USER')
vk_user = vk_api.VkApi(token=vk_user_token)


def check_city(city: str) -> dict:
    fields = {
        'country_id': 1,
        'q': city,
        'count': 1
    }
    try:
        response = vk_user.method('database.getCities', values=fields)
        return response['items']
    except vk_api.exceptions.ApiError as error:
        print(error)


def get_person_id(user_info: dict, city: int, age: int) -> object | str:
    fields = {
        'count': 1000,
        'v': 5.131,
        'city': city,
        'sex': 3 - user_info['sex'],
        'status': 6,
        'age_from': age + 0,
        'age_to': age + 0,
        'has_photo': 1
    }
    try:
        response = vk_user.method('users.search', values=fields)
        open_page_persons_id = []
        for person in response.get('items'):
            if not person['is_closed']:
                open_page_persons_id.append(person['id'])
        for person_id in open_page_persons_id:
            yield person_id
    except vk_api.exceptions.ApiError as error:
        print(error)


def get_photos(person_id: str) -> bool | list[str]:
    params = {
        'owner_id': person_id,
        'album_id': 'profile',
        'extended': 1,
        'v': 5.131
    }
    try:
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
    except vk_api.exceptions.ApiError as error:
        print(error)
