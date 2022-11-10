import argparse
import os

from dotenv import load_dotenv
import requests as requests
from terminaltables import AsciiTable


def get_vacancies(url, params=None, payload=None):
    response = requests.get(url, headers=payload, params=params)
    response.raise_for_status()

    return response.json()


def average(salary_avg: list) -> int:
    try:
        return int(sum(salary_avg) / len(salary_avg))
    except ZeroDivisionError:
        return 0


def get_statistic_by_pl(pl_vacancies: dict, source='hh') -> dict:
    pl_info = {}
    salaries = []
    for vacancy in pl_vacancies['items'] if source == 'hh' else pl_vacancies['objects']:
        vacancy_avg_salary = predict_rub_salary_hh(vacancy) if source == 'hh' else predict_rub_salary_sj(vacancy)

        if vacancy_avg_salary:
            salaries.append(vacancy_avg_salary)
        pl_info['vacancies_found'] = pl_vacancies['found'] if source == 'hh' else pl_vacancies['total']

    pl_info['vacancies_processed'] = len(salaries)
    pl_info['average_salary'] = average(salaries)

    return pl_info


def get_vacancies_from_all_pages_hh(url, params):
    pl_vacancies_data_template = get_vacancies(url, params)
    count_of_vacancies_pages = pl_vacancies_data_template['pages']

    if count_of_vacancies_pages > 0:
        pl_vacancies_data_template['items'] = []
        for page in range(count_of_vacancies_pages):
            params['page'] = page
            vacancies_from_page = get_vacancies(url, params)['items']
            pl_vacancies_data_template['items'].extend(vacancies_from_page)

    return pl_vacancies_data_template


def get_vacancies_from_all_pages_sj(url, params, payload):
    pl_vacancies_data_template = get_vacancies(url, params, payload)
    page = 0

    while get_vacancies(url, params, payload)['more']:
        pl_vacancies_data_template['objects'] = []
        params['page'] = page
        vacancies_from_page = get_vacancies(url, params, payload)['objects']
        pl_vacancies_data_template['objects'].extend(vacancies_from_page)
        page += 1

    return pl_vacancies_data_template


def draw_table(languages_info: dict, title: str):
    pl_info = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]

    for programming_lang, pl_statistic in languages_info.items():
        _ = [programming_lang, pl_statistic['vacancies_found'], pl_statistic['vacancies_processed'],
             pl_statistic['average_salary']]
        pl_info.append(_)

    table_instance = AsciiTable(pl_info, title)
    table_instance.justify_columns[4] = 'right'
    print(table_instance.table)


def predict_salary(salary_from, salary_to):
    salary = None
    if salary_from is not None and salary_to is not None:
        salary = int((salary_from + salary_to) // 2)
    elif salary_from is not None:
        salary = int(salary_from * 1.2)
    elif salary_to is not None:
        salary = int(salary_to * 0.8)

    return salary


def predict_rub_salary_sj(vacancy: dict):
    if vacancy['currency'] == 'rub':
        if vacancy['payment_from'] == 0:
            vacancy['payment_from'] = None
        if vacancy['payment_to'] == 0:
            vacancy['payment_to'] = None
        return predict_salary(vacancy['payment_from'], vacancy['payment_to'])


def predict_rub_salary_hh(vacancy: dict):
    if vacancy['salary'] and vacancy['salary']['currency'] == 'RUR':
        return predict_salary(vacancy['salary']['from'], vacancy['salary']['to'])


def hh_statistic(programming_languages: list) -> dict:
    hh_languages_info = {}
    hh_url = 'https://api.hh.ru/vacancies'
    hh_params = {"specialization": "1.221",
                 "area": "1",
                 "period": 30,
                 "text": "Python",
                 "page": 0,
                 "per_page": 100
                 }

    for programming_language in programming_languages:
        hh_params['text'] = programming_language
        pl_vacancies = get_vacancies_from_all_pages_hh(hh_url, hh_params)
        hh_languages_info[programming_language] = get_statistic_by_pl(pl_vacancies)

    return hh_languages_info


def sj_statistic(programming_languages: list, token: str) -> dict:
    sj_languages_info = {}
    sj_payload = {'X-Api-App-Id': token,
                  'Content-Type': "application/x-www-form-urlencoded"
                  }
    sj_params = {"town": 4,
                 "catalogues": 48,
                 "count": 10,
                 "keywords": "Python",
                 "srws": 1,
                 "page": 0
                 }
    sj_url = 'https://api.superjob.ru/2.0/vacancies/'

    for programming_language in programming_languages:
        sj_params["keywords"] = programming_language
        sj_vacancies = get_vacancies_from_all_pages_sj(sj_url, sj_params, sj_payload)
        sj_languages_info[programming_language] = get_statistic_by_pl(sj_vacancies, 'sj')
        sj_params["page"] = 0

    return sj_languages_info


def main():
    load_dotenv()
    sj_token = os.environ['SJ_SECRET_KEY']

    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--programming_languages", default=['Python'], nargs='*',
                        help="Salary statistics by programming languages.")
    args = parser.parse_args()

    draw_table(hh_statistic(args.programming_languages), 'HeadHunter Moscow')
    draw_table(sj_statistic(args.programming_languages, sj_token), 'SuperJob Moscow')


if __name__ == '__main__':
    main()
