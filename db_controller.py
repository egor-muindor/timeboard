try:
    import datetime
    import json
    import pymysql.cursors
except ImportError as e:
    print('Не найдены необходимые библиотеки (%s)' % e.name)
    exit(500)


class DatabaseController:
    """ Версия контроллера для базы MySQL """

    def __init__(self):
        self.__load_config__()
        self.connect = pymysql.connect(self.config['host'], self.config['user'], self.config['password'],
                                       self.config['database'], charset='utf8mb4',
                                       cursorclass=pymysql.cursors.DictCursor)

    def __load_config__(self):
        """Загружает конфигурацию базы данных"""

        def input_or_default(str, default):
            ans = input('%s (%s):' % (str, default))

            return ans if ans else default

        try:
            f = open('config.json', "r", encoding='utf-8')
            config = json.loads(f.read())
            f.close()
            if config['host'] and config['user'] and config['password'] and config['database']:
                print('Конфигурация загружена.')
            else:
                raise Exception('Конфигурация не корректная.')
        except Exception as e:
            print('Не найден файл конфигурации. Настройка нового:')
            config = {
                "host": "localhost",
                "user": "laravel",
                "password": "secret",
                "database": "timeboard"
            }
            config['host'] = input_or_default('Введите хост', config['host'])
            config['database'] = input_or_default('Введите название базы данных', config['database'])
            config['user'] = input_or_default('Введите пользователя', config['user'])
            config['password'] = input_or_default('Введите пароль', config['password'])
            print('Сохранение конфига.\n\n')
            f = open("config.json", "w", encoding='utf-8')
            f.write(json.dumps(config, ensure_ascii=False, sort_keys=True, indent=4))
            f.close()
        self.config = config

    def setup_db(self):
        """ Вызывает установку БД """
        self.__setup_db__()

    def reset_pair_data(self):
        """ Сбрасывает данные для перезаписи """
        c = self.connect.cursor()
        c.execute('''
                    DROP TABLE IF exists
                    `auditory_pair`, `group_pair`, `teacher_pair`;
                ''')
        c.execute('''
                                CREATE TABLE IF NOT EXISTS `auditory_pair` (
                                    `auditory_id` INT NOT NULL,
                                    `pair_id` INT NOT NULL,
                                    PRIMARY KEY (`auditory_id`, `pair_id`),
                                    FOREIGN KEY (`auditory_id`)
                                    REFERENCES `auditories` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
                                    FOREIGN KEY (`pair_id`)
                                    REFERENCES `pairs` (`id`) ON DELETE CASCADE ON UPDATE CASCADE) 
                                ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;''')
        c.execute('''
                                CREATE TABLE IF NOT EXISTS `teacher_pair` (
                                    `teacher_id` INT NOT NULL,
                                    `pair_id` INT NOT NULL,
                                    PRIMARY KEY (`teacher_id`, `pair_id`),
                                    FOREIGN KEY (`teacher_id`)
                                    REFERENCES `teachers` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
                                    FOREIGN KEY (`pair_id`)
                                    REFERENCES `pairs` (`id`) ON DELETE CASCADE ON UPDATE CASCADE) 
                                ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;''')
        c.execute('''
                                CREATE TABLE IF NOT EXISTS `group_pair` (
                                    `group_id` INT NOT NULL,
                                    `pair_id` INT NOT NULL,
                                    PRIMARY KEY (`group_id`, `pair_id`),
                                    FOREIGN KEY (`group_id`)
                                    REFERENCES `groups` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
                                    FOREIGN KEY (`pair_id`)
                                    REFERENCES `pairs` (`id`) ON DELETE CASCADE ON UPDATE CASCADE) 
                                ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;''')

    def drop_db(self):
        """ Удаляет все таблицы """
        c = self.connect.cursor()
        c.execute('''
            DROP TABLE IF exists
            `auditory_pair`, `group_pair`, `info`, `teacher_pair`;
        ''')
        c.execute('''
            DROP TABLE IF exists
            `auditories`, `groups`, `pairs`, `teachers`;
        ''')
        self.connect.commit()

    def __setup_db__(self):
        """ Разворачивает БД """
        c = self.connect.cursor()
        c.execute(
            '''
            CREATE TABLE IF NOT EXISTS info (
                `name` VARCHAR  (30)   NOT NULL UNIQUE,
                `status` VARCHAR  (45) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;'''
        )
        c.execute(
            '''
            CREATE TABLE IF NOT EXISTS groups (
                `id`   INT      PRIMARY KEY AUTO_INCREMENT NOT NULL 
                                  NOT NULL,
                `name` VARCHAR  (15)  NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci AUTO_INCREMENT=1;'''
        )
        c.execute('''
            CREATE TABLE IF NOT EXISTS teachers (
                `id`   INT      NOT NULL AUTO_INCREMENT,
                `name` VARCHAR  (175) NOT NULL,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci AUTO_INCREMENT=1;''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS auditories (
                `id`   INT      NOT NULL AUTO_INCREMENT,
                `name` VARCHAR  (30) NOT NULL,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci AUTO_INCREMENT=1;''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS pairs (
                `id`          INT       AUTO_INCREMENT NOT NULL,
                `subject`     VARCHAR  (200) NOT NULL,
                `type`        VARCHAR  (30)  NOT NULL,
                `date_from`   VARCHAR  (15),
                `date_to`     VARCHAR  (15),
                `pair_number` INT      NOT NULL,
                `day`         VARCHAR  (15)  NOT NULL,
                `is_session`  BIT     NOT NULL,
                `key_auditory` VARCHAR (30) NOT NULL,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci AUTO_INCREMENT=1;''')
        c.execute('''
                        CREATE TABLE IF NOT EXISTS `auditory_pair` (
                            `auditory_id` INT NOT NULL,
                            `pair_id` INT NOT NULL,
                            PRIMARY KEY (`auditory_id`, `pair_id`),
                            FOREIGN KEY (`auditory_id`)
                            REFERENCES `auditories` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
                            FOREIGN KEY (`pair_id`)
                            REFERENCES `pairs` (`id`) ON DELETE CASCADE ON UPDATE CASCADE) 
                        ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;''')
        c.execute('''
                        CREATE TABLE IF NOT EXISTS `teacher_pair` (
                            `teacher_id` INT NOT NULL,
                            `pair_id` INT NOT NULL,
                            PRIMARY KEY (`teacher_id`, `pair_id`),
                            FOREIGN KEY (`teacher_id`)
                            REFERENCES `teachers` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
                            FOREIGN KEY (`pair_id`)
                            REFERENCES `pairs` (`id`) ON DELETE CASCADE ON UPDATE CASCADE) 
                        ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;''')
        c.execute('''
                        CREATE TABLE IF NOT EXISTS `group_pair` (
                            `group_id` INT NOT NULL,
                            `pair_id` INT NOT NULL,
                            PRIMARY KEY (`group_id`, `pair_id`),
                            FOREIGN KEY (`group_id`)
                            REFERENCES `groups` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
                            FOREIGN KEY (`pair_id`)
                            REFERENCES `pairs` (`id`) ON DELETE CASCADE ON UPDATE CASCADE) 
                        ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;''')
        self.connect.commit()
        c.close()

    def insert_group(self, group):
        """ Вносит данные в таблицу groups """
        c = self.connect.cursor()
        c.execute('''
            INSERT INTO groups (name) VALUES (%s);
        ''', (group,))
        c.execute('SELECT id, name FROM groups where name=%s', (group,))
        return c.fetchone()['id']

    def insert_auditory_pair(self, auditory_id, pair_id):
        """ Вносит данные в таблицу auditory_pair """
        c = self.connect.cursor()
        c.execute('''
            INSERT INTO auditory_pair (auditory_id, pair_id) VALUES (%s, %s);
        ''', (auditory_id, pair_id))
        c.execute('SELECT auditory_id, pair_id FROM auditory_pair where auditory_id=%s and pair_id=%s',
                  (auditory_id, pair_id))
        return c.fetchone()

    def insert_group_pair(self, group_id, pair_id):
        """ Вносит данные в таблицу group_pair """
        c = self.connect.cursor()
        c.execute('''
            INSERT INTO group_pair (group_id, pair_id) VALUES (%s, %s);
        ''', (group_id, pair_id))
        c.execute('SELECT group_id, pair_id FROM group_pair where group_id=%s and pair_id=%s',
                  (group_id, pair_id))
        return c.fetchone()

    def insert_teacher_pair(self, teacher_id, pair_id):
        """ Вносит данные в таблицу teacher_pair """
        c = self.connect.cursor()
        c.execute('''
            INSERT INTO teacher_pair (teacher_id, pair_id) VALUES (%s, %s);
        ''', (teacher_id, pair_id))
        c.execute('SELECT teacher_id, pair_id FROM teacher_pair where teacher_id=%s and pair_id=%s',
                  (teacher_id, pair_id))
        return c.fetchone()

    def insert_teacher(self, teacher):
        """ Вносит данные в таблицу teachers """
        c = self.connect.cursor()
        c.execute('''
                    INSERT INTO teachers (name) VALUES (%s);
                ''', (teacher,))
        c.execute('SELECT id, name FROM teachers WHERE name=%s', (teacher,))
        return c.fetchone()['id']

    def insert_auditory(self, auditory):
        """ Вносит данные в таблицу auditories """
        c = self.connect.cursor()
        c.execute('''
                    INSERT INTO auditories (name) VALUES (%s);
                ''', (auditory,))
        c.execute('SELECT id, name FROM auditories WHERE name=%s', (auditory,))
        return c.fetchone()['id']

    def insert_pair(self, pair):
        """ Вносит данные в таблицу pairs """
        c = self.connect.cursor()
        c.execute(
            """
            SELECT `id`, `day`, `pair_number`, `date_to`, `date_from`, `type`, `subject`, `is_session`, `key_auditory`
            FROM pairs 
            WHERE `day`=%s and `pair_number`=%s and `date_to`=%s and 
            `date_from`=%s and `type`=%s and `subject`=%s and `is_session`=%s and `key_auditory`=%s
            """, pair)
        available = c.fetchone()
        if available:
            return available['id']

        c.execute('''
                    INSERT INTO `pairs` (
                      `day`,
                      `pair_number`,
                      `date_to`,
                      `date_from`,
                      `type`,
                      `subject`,
                      `is_session`,
                      `key_auditory`
                  )
                  VALUES (%s,%s,%s,%s,%s,%s,%s, %s);
                ''', pair)
        c.execute(
            """
            SELECT `id`, `day`, `pair_number`, `date_to`, `date_from`, `type`, `subject`, `is_session`,`key_auditory`
            FROM pairs WHERE `day`=%s and `pair_number`=%s and `date_to`=%s and 
            `date_from`=%s and `type`=%s and `subject`=%s and `is_session`=%s and `key_auditory`=%s""", pair)
        return c.fetchone()['id']

    def update_info(self, name, status):
        """ Вносит или обновляет информацию в системной таблице info """
        c = self.connect.cursor()
        c.execute('''
            REPLACE INTO info VALUES (%s, %s) ;
        ''', (name, status,))

    def find_teacher(self, name):
        """ Возвращает id преподавателя, если не найден - вернет False """
        c = self.connect.cursor()
        c.execute("SELECT id, name from teachers where name LIKE %s LIMIT 30", ("%{}%".format(name.title()),))
        result = c.fetchall()
        if not result:
            return False
        else:
            return result['id']

    def find_or_new_teacher(self, name):
        """ Возвращает id преподавателя, если не находит - создает нового"""
        c = self.connect.cursor()
        c.execute("SELECT id, name from teachers where name=%s", (name,))
        result = c.fetchone()
        if not result:
            return self.insert_teacher(name)
        else:
            return result['id']

    def find_or_new_teacher_pair(self, teacher_id, pair_id):
        """ Возвращает id пары и id преподавателя"""
        c = self.connect.cursor()
        c.execute('SELECT teacher_id, pair_id FROM teacher_pair where teacher_id=%s and pair_id=%s',
                  (teacher_id, pair_id))
        result = c.fetchone()
        if not result:
            return self.insert_teacher_pair(teacher_id, pair_id)
        else:
            return result

    def find_or_new_group_pair(self, group_id, pair_id):
        """Возвращает id группы и id пары"""
        c = self.connect.cursor()
        c.execute('SELECT group_id, pair_id FROM group_pair where group_id=%s and pair_id=%s',
                  (group_id, pair_id))
        result = c.fetchone()
        if not result:
            return self.insert_group_pair(group_id, pair_id)
        else:
            return result

    def find_or_new_auditory_pair(self, auditory_id, pair_id):
        """ Возвращает id аудитории и id пары"""
        c = self.connect.cursor()
        c.execute('SELECT auditory_id, pair_id FROM auditory_pair where auditory_id=%s and pair_id=%s',
                  (auditory_id, pair_id))
        result = c.fetchone()
        if not result:
            return self.insert_auditory_pair(auditory_id, pair_id)
        else:
            return result

    def find_or_new_auditory(self, auditory):
        """ Возвращает id преподавателя, если не находит - создает нового"""
        c = self.connect.cursor()
        c.execute("SELECT id, name from auditories where name=%s", (auditory,))
        result = c.fetchone()
        if not result:
            return self.insert_auditory(auditory)
        else:
            return result['id']

    def import_from_json(self, data, is_file=True):
        """ Заносит все данные из json файла или массива данных """
        if is_file:
            f = open(data, "r", encoding='utf-8')
            data = json.loads(f.read())
            f.close()
        self.reset_pair_data()
        for timeboard in data:
            if len(timeboard['group']['title']) > 15:
                continue
            group_id = self.insert_group(timeboard['group']['title'])
            for key_day, day in timeboard.get('grid').items():
                for key_pair, pair_module in day.items():
                    if not pair_module:
                        continue
                    for pair in pair_module:
                        try:
                            if 'date_to' not in pair or 'date_from' not in pair:
                                pair['date_to'] = ''
                                pair['date_from'] = ''
                            pair_data = (
                                key_day,
                                key_pair,
                                pair['date_to'],
                                pair['date_from'],
                                pair['type'],
                                pair['subject'],
                                timeboard['isSession'],
                                pair['auditories'][0]['title']
                            )
                            pair_id = self.insert_pair(pair_data)
                            self.find_or_new_group_pair(group_id, pair_id)
                            for auditory in pair['auditories']:
                                auditory_id = self.find_or_new_auditory(auditory['title'])
                                self.find_or_new_auditory_pair(auditory_id, pair_id)
                            for teacher in pair['teacher'].split(', '):
                                if teacher == '':
                                    continue
                                teacher_id = self.find_or_new_teacher(teacher)
                                self.find_or_new_teacher_pair(teacher_id, pair_id)
                            # pair['auditories']
                        except():
                            print(pair)

        self.connect.commit()

    def exit(self):
        """ Необходимо выполнить после завершения действий с БД """
        try:
            self.update_info('update_date', '%s' % datetime.date.today())
            self.connect.commit()
            self.connect.close()
            print('Finish')
            return True
        except():
            return False


if __name__ == '__main__':
    """ Использовалось для тестов, пусть тут лежит """
    db = DatabaseController()
    db.reset_pair_data()
    db.exit()
