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


def predict_rub_salary(vacancy: dict):
    if vacancy['salary'] and vacancy['salary']['currency'] == 'RUR':
        if vacancy['salary']['from'] is not None and vacancy['salary']['to'] is not None:
            return int((vacancy['salary']['from'] + vacancy['salary']['to']) // 2)
        elif vacancy['salary']['from'] is not None:
            return int(vacancy['salary']['from'] * 1.2)
        else:
            return int(vacancy['salary']['to'] * 0.8)
    else:
        return


def average(salary_avg: list) -> int:
    return int(sum(salary_avg) / len(salary_avg))


def get_statistic_by_pl(pl_vacancies: dict) -> dict:
    pl_info = {}
    salaries = []
    for vacancy in pl_vacancies['items']:
        vacancy_avg_salary = predict_rub_salary(vacancy)
        if vacancy_avg_salary:
            salaries.append(vacancy_avg_salary)
        pl_info['vacancies_found'] = pl_vacancies['found']

    pl_info['vacancies_processed'] = len(salaries)
    pl_info['average_salary'] = average(salaries)

    return pl_info


def main():
    programming_languages = ['Python', 'Java', 'Javascript']
    languages_info = {}
    url = 'https://api.hh.ru/vacancies'

    for pl in programming_languages:
        pl_vacancies = get_hh_vacancies(url, pl)  # common_func.get_json_from_file('Python.json')
        languages_info[pl] = get_statistic_by_pl(pl_vacancies)

    print(languages_info)


if __name__ == '__main__':
    main()
