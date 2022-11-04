import requests as requests

import common_func


def get_hh_vacancies(url: str, search_text) -> dict:
    payload = {"specialization": "1.221",
               "area": "1",
               "period": 30,
               "text": search_text
               }
    response = requests.get(url, params=payload)
    response.raise_for_status()

    return response.json()


def get_vacancies_count_by_pl(url: str, programming_languages: list) -> dict:
    pl_vacancies_count = {}
    for programming_language in programming_languages:
        hh_vacancies = get_hh_vacancies(url, programming_language)
        common_func.save_to_json(hh_vacancies, f'{programming_language}.json')
        pl_vacancies_count[programming_language] = hh_vacancies['found']

    return pl_vacancies_count


def main():
    programming_languages = ['Python', 'Java', 'Javascript']
    url = 'https://api.hh.ru/vacancies'

    print(get_vacancies_count_by_pl(url, programming_languages))


if __name__ == '__main__':
    main()
