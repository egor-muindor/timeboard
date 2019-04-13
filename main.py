try:
    import json
    import time
    from operator import itemgetter
    from timeboard import Timeboard
except ImportError as e:

    print('Не найдены необходимые библиотеки (%s)' % e.name)
    exit(500)


def download_timeboards():
    all_timeboads = []
    t = Timeboard()

    for group_id in t.group_list:
        success = False
        c = 0
        while not success:
            try:
                data = t.disassemble_group(group_id)
                if not data:
                    print('Расписание группы %s отсутствует' % group_id)
                    break
                all_timeboads.append(
                    (
                        group_id,
                        data
                    )
                )
                print('Расписание группы %s успешно скачано' % group_id)
                success = True
            except():
                if c < 3:
                    c += 1
                    print('Расписание группы %s не удалось скачать' % group_id)
                    time.sleep(5)
                else:
                    success = True
                    print('Расписание группы %s пропущено' % group_id)

    f = open("data.json", "w", encoding='utf-8')
    f.write(json.dumps(all_timeboads, ensure_ascii=False, sort_keys=True, indent=4))
    f.close()
    print('Расписания групп успешно скачаны')


def convert_day(day):
    days = {
        '1': 'Понедельник',
        '2': 'Вторник',
        '3': 'Среда',
        '4': 'Четверг',
        '5': 'Пятница',
        '6': 'Суббота',
    }
    if day in days:
        return days[day]
    else:
        return day


def find_professor(name=''):
    result = []
    pairs = {
        '1': '9:00-10:30',
        '2': '10:40-12:10',
        '3': '12:20-13:50',
        '4': '14:30-16:00',
        '5': '16:10-17:40',
        '6': '17:50-19:20',
        '7': '19:30-21:00'
    }

    f = open("data.json", "r", encoding='utf-8')
    data = json.loads(f.read())
    f.close()

    for group in data:
        for pair in group[1]:
            if name.lower() in pair['teacher'].lower():
                result.append(
                    {
                        'professor_name': pair['teacher'],
                        'group_id': group[0],
                        'day_id': pair['day'],
                        'day': convert_day(pair['day']),
                        'number_pair': pair['number_pair'],
                        'pair_time': pairs[pair['number_pair']],
                        'auditory': ' '.join(pair['pair']),
                    }
                )

    result.sort(key=itemgetter('day_id', 'number_pair'))

    if result:
        for each in result:
            print(
                'Пара у {professor_name} будет в {day}, в {pair_time}, '
                'в аудитории {auditory}. Группа "{group_id}"'
                    .format_map(each)
            )
        return True
    else:
        print('Пары не найдены')
        return False


def menu():
    print(
        '''
        Меню:
        0) Выход
        1) Найти пары преподавателя по части ФИО
        2) Обновить базу
        ''')
    choice = input()
    if choice in '0':
        exit(0)
    elif choice in '1':
        name = input('Введите часть ФИО преподавателя: ')
        find_professor(name)
    elif choice in '2':
        print('Обновление базы займет какое то время, пожалуйста подождите')
        download_timeboards()


try:
    file = open('data.json')
    file.close()
except IOError:
    print('База не найдена, началась загрузка..\n')
    download_timeboards()
else:
    print('База обнаружена')
0
while True:
    menu()
