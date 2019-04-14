import json
import sqlite3
import time


class DatabaseController:

    def __init__(self, db_name):
        self.db_name = db_name
        self.connect = sqlite3.connect(db_name)
        self.__setup_db__()

    def __setup_db__(self):
        c = self.connect.cursor()
        c.execute('DROP TABLE IF EXISTS pairs;')
        self.connect.commit()
        c.execute('DROP TABLE IF EXISTS teachers;')
        self.connect.commit()
        c.execute('DROP TABLE IF EXISTS groups;')
        self.connect.commit()
        c.execute('DROP INDEX IF EXISTS pairs.pair_index;')
        self.connect.commit()
        c.execute(
            '''
            CREATE TABLE IF NOT EXISTS groups (
                id   INTEGER      PRIMARY KEY AUTOINCREMENT NOT NULL 
                                  NOT NULL,
                name STRING (15)  NOT NULL
            );'''
        )
        self.connect.commit()
        c.execute('''
            CREATE TABLE IF NOT EXISTS teachers (
                id   INTEGER      PRIMARY KEY AUTOINCREMENT NOT NULL 
                                  NOT NULL,
                name STRING (150) NOT NULL
            );''')
        self.connect.commit()
        c.execute('''
            CREATE TABLE IF NOT EXISTS pairs (
                id          INTEGER      PRIMARY KEY AUTOINCREMENT NOT NULL 
                                         NOT NULL,
                auditory    STRING (25)  NOT NULL,
                subject     STRING (100) NOT NULL,
                type        STRING (30)  NOT NULL,
                data_from   STRING (15),
                date_to     STRING (15),
                pair_number INTEGER      NOT NULL,
                day         STRING (15)  NOT NULL,
                is_session  BOOLEAN      NOT NULL,
                group_id    INTEGER      REFERENCES groups (id) ON DELETE CASCADE
                                         NOT NULL,
                teacher_id  INTEGER      REFERENCES teachers (id) ON DELETE CASCADE
                                         NOT NULL
            );''')
        self.connect.commit()
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

        c = self.connect.cursor()
        c.execute('''
            INSERT INTO groups (name) VALUES (?);
        ''', (group,))
        self.connect.commit()
        c.execute('SELECT id, name FROM groups where name=?', (group,))
        result = c.fetchone()[0]
        c.close()
        return result

    def insert_teacher(self, teacher):

        c = self.connect.cursor()
        c.execute('''
                    INSERT INTO teachers (name) VALUES (?);
                ''', (teacher,))
        self.connect.commit()
        c.execute('SELECT id, name FROM teachers WHERE name=?', (teacher,))
        result = c.fetchone()[0]
        c.close()
        return result

    def insert_pair(self, pair):

        c = self.connect.cursor()
        c.execute('''
                    INSERT INTO pairs (
                      teacher_id,
                      group_id,
                      day,
                      pair_number,
                      date_to,
                      data_from,
                      type,
                      subject,
                      auditory,
                      is_session
                  )
                  VALUES (?,?,?,?,?,?,?,?,?,?);
                ''', pair)
        self.connect.commit()
        c.close()

    def find_teacher(self, name):
        c = self.connect.cursor()
        c.execute("SELECT id, name from teachers where name=?", (name,))
        self.connect.commit()
        result = c.fetchall()
        c.close()
        if not result:
            return False
        else:
            return result

    def find_or_new_teacher(self, name):
        c = self.connect.cursor()
        c.execute("SELECT id, name from teachers where name=?", (name,))
        self.connect.commit()
        result = c.fetchone()
        c.close()
        if not result:
            return self.insert_teacher(name)
        else:
            return result[0]

    def import_from_json(self, file):

        f = open(file, "r", encoding='utf-8')
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


t = time.time()
db = DatabaseController('my.db')
db.import_from_json('all_data.json')
print('Finish')
print(time.time() - t)
