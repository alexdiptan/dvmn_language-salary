import logging

import requests as requests

import common_func


def get_hh_vacancies(url: str, search_text: str, page: int = 0, per_page: int = 100) -> dict:
    payload = {"specialization": "1.221",
               "area": "1",
               "period": 30,
               "text": search_text,
               "page": page,
               "per_page": per_page
               }
    response = requests.get(url, params=payload)
    response.raise_for_status()

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


def get_vacancies_from_all_pages(url, pl):
    pl_vacancies_data_template = get_hh_vacancies(url, pl)
    count_of_vacancies_pages = pl_vacancies_data_template['pages']

    if count_of_vacancies_pages > 0:
        pl_vacancies_data_template['items'] = []
        for page in range(count_of_vacancies_pages):
            logging.info(f'Programming language is: {pl}, {page} page of {count_of_vacancies_pages}')
            vacancies_from_page = get_hh_vacancies(url, pl, page)['items']
            pl_vacancies_data_template['items'].extend(vacancies_from_page)

    return pl_vacancies_data_template


def main():
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
    programming_languages = ['Python', 'Java', 'Javascript']
    url = 'https://api.hh.ru/vacancies'
    languages_info = {}

    for pl in programming_languages:
        pl_vacancies = get_vacancies_from_all_pages(url, pl)
        languages_info[pl] = get_statistic_by_pl(pl_vacancies)
        common_func.save_to_json(pl_vacancies, f'{pl}.json')

    logging.info(languages_info)


if __name__ == '__main__':
    main()
