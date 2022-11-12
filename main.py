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


def get_statistic_by_programming_language(vacancies: dict, vacancies_found, source='hh') -> dict:
    programming_language_statistic = {}
    salaries = []
    for vacancy in vacancies:
        vacancy_avg_salary = predict_rub_salary_hh(vacancy) if source == 'hh' else predict_rub_salary_sj(vacancy)

        if vacancy_avg_salary:
            salaries.append(vacancy_avg_salary)

        programming_language_statistic['vacancies_found'] = vacancies_found

    programming_language_statistic['vacancies_processed'] = len(salaries)
    programming_language_statistic['average_salary'] = average(salaries)

    return programming_language_statistic


def get_vacancies_from_all_pages_hh(url, params):
    vacancies_search_result = get_vacancies(url, params)
    count_of_pages = vacancies_search_result['pages']

    if not count_of_pages:
        return
    vacancies_search_result['items'] = []
    for page in range(count_of_pages):
        params['page'] = page
        vacancies_from_page = get_vacancies(url, params)['items']
        vacancies_search_result['items'].extend(vacancies_from_page)

    return vacancies_search_result


def get_vacancies_from_all_pages_sj(url, params, payload):
    vacancies_search_result = get_vacancies(url, params, payload)
    page = 0

    while get_vacancies(url, params, payload)['more']:
        vacancies_search_result['objects'] = []
        params['page'] = page
        vacancies_from_page = get_vacancies(url, params, payload)['objects']
        vacancies_search_result['objects'].extend(vacancies_from_page)
        page += 1

    return vacancies_search_result


def draw_table(languages_statistic: dict, title: str):
    programming_language_data_for_table = [['Язык программирования', 'Вакансий найдено',
                                            'Вакансий обработано', 'Средняя зарплата']]

    for programming_lang, statistic_by_programming_language in languages_statistic.items():
        _ = [programming_lang, statistic_by_programming_language['vacancies_found'],
             statistic_by_programming_language['vacancies_processed'],
             statistic_by_programming_language['average_salary']]
        programming_language_data_for_table.append(_)

    table_instance = AsciiTable(programming_language_data_for_table, title)
    table_instance.justify_columns[4] = 'right'
    print(table_instance.table)


def predict_salary(salary_from, salary_to):
    salary = None
    if salary_from and salary_to:
        salary = int((salary_from + salary_to) // 2)
    elif salary_from:
        salary = int(salary_from * 1.2)
    elif salary_to:
        salary = int(salary_to * 0.8)

    return salary


def predict_rub_salary_sj(vacancy: dict):
    if vacancy['currency'] != 'rub':
        return
    if not vacancy['payment_from']:
        vacancy['payment_from'] = None
    if not vacancy['payment_to']:
        vacancy['payment_to'] = None
    return predict_salary(vacancy['payment_from'], vacancy['payment_to'])


def predict_rub_salary_hh(vacancy: dict):
    if vacancy['salary'] and vacancy['salary']['currency'] == 'RUR':
        return predict_salary(vacancy['salary']['from'], vacancy['salary']['to'])


def get_hh_statistic(programming_languages: list) -> dict:
    professional_code_programmer = '1.221'
    code_of_moscow_city = '1'
    search_vacancies_period_in_days = 30
    vacancies_count_on_page = 100
    start_from_page = 0

    hh_statistic_by_languages = {}
    hh_url = 'https://api.hh.ru/vacancies'
    hh_params = {"specialization": professional_code_programmer,
                 "area": code_of_moscow_city,
                 "period": search_vacancies_period_in_days,
                 "text": "Python",
                 "page": start_from_page,
                 "per_page": vacancies_count_on_page
                 }

    for programming_language in programming_languages:
        hh_params['text'] = programming_language
        vacancies = get_vacancies_from_all_pages_hh(hh_url, hh_params)
        hh_statistic_by_languages[programming_language] = get_statistic_by_programming_language(vacancies['items'],
                                                                                                vacancies['found'])

    return hh_statistic_by_languages


def get_sj_statistic(programming_languages: list, token: str) -> dict:
    code_of_moscow_city = 4
    professional_code_programmer = 48
    vacancies_count_on_page = 10
    start_from_page = 0
    search_text_in_heading = 1

    sj_statistic_by_languages = {}
    sj_payload = {'X-Api-App-Id': token,
                  'Content-Type': "application/x-www-form-urlencoded"
                  }
    sj_params = {"town": code_of_moscow_city,
                 "catalogues": professional_code_programmer,
                 "count": vacancies_count_on_page,
                 "keywords": "Python",
                 "srws": search_text_in_heading,
                 "page": start_from_page
                 }
    sj_url = 'https://api.superjob.ru/2.0/vacancies/'

    for programming_language in programming_languages:
        sj_params["keywords"] = programming_language
        sj_vacancies = get_vacancies_from_all_pages_sj(sj_url, sj_params, sj_payload)
        sj_statistic_by_languages[programming_language] = get_statistic_by_programming_language(sj_vacancies['objects'],
                                                                                                sj_vacancies['total'],
                                                                                                'sj')
        sj_params["page"] = 0

    return sj_statistic_by_languages


def main():
    load_dotenv()
    sj_token = os.environ['SJ_SECRET_KEY']

    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--programming_languages", default=['Python'], nargs='*',
                        help="Salary statistics by programming languages.")
    args = parser.parse_args()

    draw_table(get_hh_statistic(args.programming_languages), 'HeadHunter Moscow')
    draw_table(get_sj_statistic(args.programming_languages, sj_token), 'SuperJob Moscow')


if __name__ == '__main__':
    main()
