try:
    from db_controller import DatabaseController
    from timeboard import Timeboard
    import json
except ImportError as e:
    print('Не найдены необходимые библиотеки (%s)' % e.name)
    exit(500)

if __name__ == '__main__':
    t = Timeboard()
    data = t.download_all_groups(debug=False)  # debug включает вывод состояния загрузки в %
    # f = open("data.json", "w", encoding='utf-8')
    # f.write(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4))
    # f.close()
    db = DatabaseController()
    db.import_from_json(data, is_file=True)  # is_file=True если в аттрибуте data передается json файл
    db.exit()
    exit(0)
