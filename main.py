import requests as requests

import common_func


def get_hh_vacancies(url: str) -> dict:
    payload = {"specialization": "1.221",
               "area": "1",
               "period": 30,
               "text": "Python"
               }
    response = requests.get(url, params=payload)
    response.raise_for_status()

    return response.json()


def main():
    url = 'https://api.hh.ru/vacancies'
    common_func.save_to_json(get_hh_vacancies(url), '1.json')
    print(get_hh_vacancies(url)['found'])


if __name__ == '__main__':
    main()