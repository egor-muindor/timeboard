try:
    import requests
except ImportError as e:

    print('Не найдены необходимые библиотеки (%s)' % e.name)
    exit(500)


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

    def get_timeboard_by_group_id(self, id, session=0):
        headers = {
            'cookie': self.cookies,
            'Referer': 'https://rasp.dmami.ru/site/',
        }
        group = {
            'session': session,
            'group': id,
        }
        try:
            timeboard = self.session.get("https://rasp.dmami.ru/site/group", headers=headers, params=group).json()
        except:
            return False

        if timeboard['status'] == 'error':
            return False

        return timeboard

    def download_all_groups(self, session=0):
        groups = self.group_list
        result = []
        counter = 0
        for group in groups:
            data = self.get_timeboard_by_group_id(group, session)
            counter += 1
            print('Прогресс: {}/100%'.format(round(counter / len(groups) * 100, 2)))
            if not data:
                continue
            result.append(data)
        print('Загрузка завершена')
        return result

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
