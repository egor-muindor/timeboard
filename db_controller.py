try:
    import datetime
    import json
    import sqlite3
except ImportError as e:
    print('Не найдены необходимые библиотеки (%s)' % e.name)
    exit(500)


class DatabaseController:

    def __init__(self, db_name):
        self.db_name = db_name
        self.connect = sqlite3.connect(db_name)
        self.__setup_db__()

    def __setup_db__(self):
        """ Делает сброс БД, кроме таблицы info """
        c = self.connect.cursor()
        c.execute('PRAGMA foreign_keys = ON;')
        c.execute('DROP TABLE IF EXISTS pairs;')
        c.execute('DROP TABLE IF EXISTS teachers;')
        c.execute('DROP TABLE IF EXISTS groups;')
        c.execute('DROP INDEX IF EXISTS pairs.pair_index;')
        self.connect.commit()
        c.execute(
            '''
            CREATE TABLE IF NOT EXISTS info (
                name STRING (30)   NOT NULL UNIQUE,
                status STRING (45) NOT NULL
            );'''
        )
        c.execute(
            '''
            CREATE TABLE IF NOT EXISTS groups (
                id   INTEGER      PRIMARY KEY AUTOINCREMENT NOT NULL 
                                  NOT NULL,
                name STRING (15)  NOT NULL
            );'''
        )
        c.execute('''
            CREATE TABLE IF NOT EXISTS teachers (
                id   INTEGER      PRIMARY KEY AUTOINCREMENT NOT NULL 
                                  NOT NULL,
                name STRING (175) NOT NULL
            );''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS pairs (
                id          INTEGER      PRIMARY KEY AUTOINCREMENT NOT NULL 
                                         NOT NULL,
                auditory    STRING (25)  NOT NULL,
                subject     STRING (100) NOT NULL,
                type        STRING (30)  NOT NULL,
                date_from   STRING (15),
                date_to     STRING (15),
                pair_number INTEGER      NOT NULL,
                day         STRING (15)  NOT NULL,
                is_session  BOOLEAN      NOT NULL,
                group_id    INTEGER      REFERENCES groups (id) ON DELETE CASCADE
                                         NOT NULL,
                teacher_id  INTEGER      REFERENCES teachers (id) ON DELETE CASCADE
                                         NOT NULL
            );''')
        c.execute('''
        CREATE INDEX IF NOT EXISTS pair_index ON pairs (
            id ASC,
            auditory ASC,
            pair_number ASC,
            group_id ASC,
            teacher_id ASC
        );''')
        self.connect.commit()
        c.close()

    def insert_group(self, group):
        """ Вносит данные в таблицу groups """
        c = self.connect.cursor()
        c.execute('''
            INSERT INTO groups (name) VALUES (?);
        ''', (group,))
        c.execute('SELECT id, name FROM groups where name=?', (group,))
        return c.fetchone()[0]

    def insert_teacher(self, teacher):
        """ Вносит данные в таблицу teachers """
        c = self.connect.cursor()
        c.execute('''
                    INSERT INTO teachers (name) VALUES (?);
                ''', (teacher,))
        c.execute('SELECT id, name FROM teachers WHERE name=?', (teacher,))
        return c.fetchone()[0]

    def insert_pair(self, pair):
        """ Вносит данные в таблицу pairs """
        c = self.connect.cursor()
        c.execute('''
                    INSERT INTO pairs (
                      teacher_id,
                      group_id,
                      day,
                      pair_number,
                      date_to,
                      date_from,
                      type,
                      subject,
                      auditory,
                      is_session
                  )
                  VALUES (?,?,?,?,?,?,?,?,?,?);
                ''', pair)

    def update_info(self, name, status):
        """ Вносит или обновляет информацию в системной таблице info """
        c = self.connect.cursor()
        c.execute('''
            INSERT OR REPLACE INTO info VALUES (?, ?) ;
        ''', (name, status,))

    def find_teacher(self, name):
        """ Возвращает id преподавателя, если не найден - вернет False """
        c = self.connect.cursor()
        c.execute("SELECT id, name from teachers where name LIKE ? LIMIT 30", ("%{}%".format(name.title()),))
        result = c.fetchall()
        if not result:
            return False
        else:
            return result

    def find_or_new_teacher(self, name):
        """ Возвращает id преподавателя, если не находит - создает нового"""
        c = self.connect.cursor()
        c.execute("SELECT id, name from teachers where name=?", (name,))
        result = c.fetchone()
        if not result:
            return self.insert_teacher(name)
        else:
            return result[0]

    def import_from_json(self, data, is_file=True):
        """ Заносит все данные из json файла или массива данных """
        if is_file:
            f = open(data, "r", encoding='utf-8')
            data = json.loads(f.read())
            f.close()
        for timeboard in data:
            group_id = self.insert_group(timeboard['group']['title'])
            for key_day, day in timeboard.get('grid').items():
                for key_pair, pair_module in day.items():
                    if not pair_module:
                        continue
                    for pair in pair_module:
                        teachers = pair['teacher'].split(', ')
                        for teacher in teachers:
                            if teacher == '':
                                continue
                            teacher_id = self.find_or_new_teacher(teacher)
                            try:
                                if 'date_to' not in pair or 'date_from' not in pair:
                                    pair['date_to'] = ''
                                    pair['date_from'] = ''
                                pair_data = (
                                    teacher_id,
                                    group_id,
                                    key_day,
                                    key_pair,
                                    pair['date_to'],
                                    pair['date_from'],
                                    pair['type'],
                                    pair['subject'],
                                    ' '.join([i['title'] for i in pair['auditories']]),
                                    timeboard['isSession']
                                )
                                self.insert_pair(pair_data)
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
    db = DatabaseController('my.db')
    db.import_from_json('all_data.json')
    db.exit()