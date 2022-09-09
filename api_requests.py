import requests


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
