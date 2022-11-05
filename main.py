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


def predict_rub_salary(vacancy: dict):
    print(vacancy['salary'])
    if vacancy['salary'] and vacancy['salary']['currency'] == 'RUR':
        if vacancy['salary']['from'] is not None and vacancy['salary']['to'] is not None:
            return (vacancy['salary']['from'] + vacancy['salary']['to']) // 2
        elif vacancy['salary']['from'] is not None:
            return vacancy['salary']['from'] * 1.2
        else:
            return vacancy['salary']['to'] * 0.8
    else:
        return


def main():
    programming_languages = ['Python', 'Java', 'Javascript']
    url = 'https://api.hh.ru/vacancies'
    python_vacancies = get_hh_vacancies(url, 'Python') #common_func.get_json_from_file('Python.json')

    for vacancy in python_vacancies['items']:
        print(predict_rub_salary(vacancy))

    # print(get_vacancies_count_by_pl(url, programming_languages))


if __name__ == '__main__':
    main()
