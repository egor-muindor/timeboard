try:
    from db_controller import DatabaseController
    from timeboard import Timeboard
except ImportError as e:
    print('Не найдены необходимые библиотеки (%s)' % e.name)
    exit(500)

if __name__ == '__main__':
    db_name = 'my.db'
    t = Timeboard()
    data = t.download_all_groups(debug=True)  # debug включает вывод состояния загрузки в %
    db = DatabaseController(db_name)
    db.import_from_json(data, is_file=False)  # is_file=True если в аттрибуте data передается json файл
    db.exit()
    exit(200)
