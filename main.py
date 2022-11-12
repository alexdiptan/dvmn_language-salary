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
    programming_language_statistic = {}
    salaries = []
    for vacancy in pl_vacancies['items'] if source == 'hh' else pl_vacancies['objects']:
        vacancy_avg_salary = predict_rub_salary_hh(vacancy) if source == 'hh' else predict_rub_salary_sj(vacancy)

        if vacancy_avg_salary:
            salaries.append(vacancy_avg_salary)

        programming_language_statistic['vacancies_found'] = pl_vacancies['found'] if source == 'hh' else pl_vacancies['total']

    programming_language_statistic['vacancies_processed'] = len(salaries)
    programming_language_statistic['average_salary'] = average(salaries)

    return programming_language_statistic


def get_vacancies_from_all_pages_hh(url, params):
    vacancies_search_result = get_vacancies(url, params)
    count_of_pages = vacancies_search_result['pages']

    if count_of_pages > 0:
        vacancies_search_result['items'] = []
        for page in range(count_of_pages):
            params['page'] = page
            vacancies_from_page = get_vacancies(url, params)['items']
            vacancies_search_result['items'].extend(vacancies_from_page)

    return vacancies_search_result


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
        pl_vacancies = get_vacancies_from_all_pages_hh(hh_url, hh_params)
        hh_statistic_by_languages[programming_language] = get_statistic_by_pl(pl_vacancies)

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
        sj_statistic_by_languages[programming_language] = get_statistic_by_pl(sj_vacancies, 'sj')
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
