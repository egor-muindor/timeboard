import requests


class Timeboard():

    def __init__(self):
        self.cookies = self.get_cookies()
        self.session = requests.Session()
        self.session.headers.update({'cookie': self.cookies})
        self.group_list = self.get_group_list()

    def get_cookies(self):
        main_html = requests.get("https://rasp.dmami.ru").text
        cut_1 = main_html.find('document.cookie="') + len('document.cookie="')
        cut_2 = main_html.find(';Path=')

        return main_html[cut_1:cut_2]

    def get_group_list(self):
        group_list = self.session.get("https://rasp.dmami.ru/groups-list.json").json()['groups']

        return group_list

    def get_timeboard_by_group_id(self, id):
        headers = {
            'cookie': self.cookies,
            'Referer': 'https://rasp.dmami.ru/site/',
        }
        group = {
            'session': 0,
            'group': id,
        }
        timeboard = self.session.get("https://rasp.dmami.ru/site/group", headers=headers, params=group).json()

        if timeboard['status'] == 'error':
            return False

        return timeboard

    def disassemble_group(self, id):
        group = self.get_timeboard_by_group_id(id)
        if not group:
            return False
        t_list = []
        for key_day, day in group.get('grid').items():
            for key_pair, pair in day.items():
                if not pair:
                    continue

                last_module = len(pair) - 1
                teacher = pair[last_module]['teacher']
                if teacher != '':
                    t_list.append(
                        {
                            'teacher': teacher,
                            'pair': [i['title'] for i in pair[last_module]['auditories']],
                            'day': key_day,
                            'number_pair': key_pair,
                        }
                    )

        return t_list
