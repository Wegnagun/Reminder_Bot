import requests

from constants import API_URL


def ask_api(text, opt):
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
    url = f'{API_URL}followers/'
    headers = {"Authorization": "Bearer " + token}
    data = {"username": username}
    response = requests.delete(url=url, data=data, headers=headers)
    answer = {'code': response.status_code, 'message': response.json()}
    # if response.status_code == 400:
    #     raise requests.RequestException(
    #         'Вы уже зарегистрированы!'
    #     )
    return answer
