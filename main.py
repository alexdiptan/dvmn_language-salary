import requests as requests


def get_hh_vacancies(url: str):
    payload = {"specialization": "1.221",
               "area": "1",
               "period": 30,
               "text": "Программист"
               }
    response = requests.get(url, params=payload)
    response.raise_for_status()

    print(response.json())


def main():
    url = 'https://api.hh.ru/vacancies'
    get_hh_vacancies(url)


if __name__ == '__main__':
    main()