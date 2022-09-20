import requests

from constants import API_URL


def get_weather(text, opt):
    try:
        response = requests.get(
            f'https://api.openweathermap.org/data/2.5/weather?q={text}'
            f'&appid={opt}&units=metric')
        answer = {'code': response.status_code, 'message': response.json()}
    except Exception as error:
        message = {'error': error,
                   'message': '\U00002620 Проверьте город! \U00002620'}
        return message
    else:
        return answer


def api_register_follower(username, token):
    url = f'{API_URL}followers/'
    headers = {"Authorization": "Bearer " + token}
    data = {"username": username}
    response = requests.post(url=url, data=data, headers=headers)
    answer = {'code': response.status_code, 'message': response.json()}
    if response.status_code == 400:
        raise requests.RequestException(
            'Вы уже зарегистрированы!'
        )
    return answer


def api_unfollow(username, token):
    url = f'{API_URL}followers/{username}'
    headers = {"Authorization": "Bearer " + token}
    response = requests.delete(url=url, headers=headers)
    answer = {'code': response.status_code}
    if response.status_code == 404:
        raise requests.RequestException(
            'Вас нет в подписках!'
        )
    return answer


def get_followers(token):
    url = f'{API_URL}followers/'
    headers = {"Authorization": "Bearer " + token}
    response = requests.get(url=url, headers=headers)
    return response


def add_birthday(token, name, date, owner_id):
    url = f'{API_URL}birthdays/'
    headers = {"Authorization": "Bearer " + token}
    data = {"name": name, "date": date, "owner": owner_id}
    response = requests.post(url=url, data=data, headers=headers)
    answer = {'code': response.status_code, 'message': response.json()}
    return answer
