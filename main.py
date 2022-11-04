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
    print(f'Search string is: {search_text}, {response.status_code=}')

    return response.json()


def get_vacancies_count_by_pl(url: str, search_strings: list) -> dict:
    pl_vacancies_count = {}
    for search_string in search_strings:
        hh_vacancies = get_hh_vacancies(url, search_string)
        # common_func.save_to_json(hh_vacancies, f'{programming_language}.json')
        pl_vacancies_count[search_string] = hh_vacancies['found']

    return pl_vacancies_count


def main():
    programming_languages = ['Python', 'Java', 'Javascript']
    url = 'https://api.hh.ru/vacancies'
    python_vacancies = common_func.get_json_data_from_file('Python.json')


    # print(get_vacancies_count_by_pl(url, programming_languages))


if __name__ == '__main__':
    main()
