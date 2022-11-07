import argparse
import logging

import requests as requests


def get_vacancy_sj(url, payload=None, params=None):
    response = requests.get(url, headers=payload, params=params)
    response.raise_for_status()

    return response.json()


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


def average(salary_avg: list) -> int:
    return int(sum(salary_avg) / len(salary_avg))


def get_statistic_by_pl(pl_vacancies: dict) -> dict:
    pl_info = {}
    salaries = []
    for vacancy in pl_vacancies['items']:
        vacancy_avg_salary = predict_rub_salary_hh(vacancy)
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
            vacancies_from_page = get_hh_vacancies(url, pl, page)['items']
            pl_vacancies_data_template['items'].extend(vacancies_from_page)

    return pl_vacancies_data_template


def beautify_output(languages_info: dict):
    language_beautified_output = ''

    for language_name, language_info in languages_info.items():
        language_beautified_output = (f"\n---Programming language statistic---\n"
                                      f"Programming language is: {language_name} \n"
                                      f"vacancies_found: {language_info['vacancies_found']} \n"
                                      f"vacancies_processed: {language_info['vacancies_processed']} \n"
                                      f"average_salary: {language_info['average_salary']}")

    return language_beautified_output


def predict_salary(salary_from, salary_to):
    if (salary_from != 0 or salary_from is not None) and (salary_to != 0 or salary_to is not None):
        return int((salary_from + salary_to) // 2)
    elif salary_from != 0 or salary_from is not None:
        return int(salary_from * 1.2)
    elif salary_to != 0 or salary_to is not None:
        return int(salary_to * 0.8)
    else:
        return


def predict_rub_salary_sj(vacancy: dict):
    if vacancy['currency'] == 'rub':
        return predict_salary(vacancy['payment_from'], vacancy['payment_to'])


def predict_rub_salary_hh(vacancy: dict):
    if vacancy['salary'] and vacancy['salary']['currency'] == 'RUR':
        return predict_salary(vacancy['salary']['from'], vacancy['salary']['to'])


def main():
    sj_token = 'v3.r.14477198.2544ffb7d2a73740f4d56682c83df10ba1d9a4f4.525999755030bd53f285987ff9139e64c752f163'
    sj_payload = {'X-Api-App-Id': sj_token,
                  'Content-Type': "application/x-www-form-urlencoded"
                  }
    sj_params = {"town": 4,
                 "catalogues": 48,
                 }
    sj_url = 'https://api.superjob.ru/2.0/vacancies/'

    hh_url = 'https://api.hh.ru/vacancies'

    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--programming_languages", default=['Python'], nargs='*',
                        help="Salary statistics by programming languages.")
    args = parser.parse_args()

    sj_vacancies = get_vacancy_sj(sj_url, sj_payload, sj_params)['objects']

    for sj_vacancy in sj_vacancies:
        # print(sj_vacancy)
        print(sj_vacancy['profession'], predict_rub_salary_sj(sj_vacancy))

    logging.info(f'Start receiving data')

    # for pl in args.programming_languages:
    #     languages_info = {}
    #     pl_vacancies = get_vacancies_from_all_pages(url, pl)
    #     languages_info[pl] = get_statistic_by_pl(pl_vacancies)
    #     logging.info(beautify_output(languages_info))

    logging.info(f'All data processed. Exit.')


if __name__ == '__main__':
    main()
