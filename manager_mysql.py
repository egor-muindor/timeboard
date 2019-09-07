try:
    from db_controller import DatabaseController
    import json
except ImportError as e:
    print('Не найдены необходимые библиотеки (%s)' % e.name)
    exit(500)

db = DatabaseController()

print('==== Менеджер базы данных парсера расписания ====\n'
      '\tМеню:\n'
      '\t1) Развернуть схему базы данных\n'
      '\t2) Удалить схему базы данных\n'
      '\t3) Выход\n\n')

while True:
    choice = input('Выберите опцию:\n')
    if choice == '1':
        try:
            db.setup_db()
            print('Схема успешно развернута!')
            print('Выход из программы.')
            exit(0)
        except Exception as e:
            print('При развертывании схемы возникла непредвиденная ошибка.')
            print(e)
    elif choice == '2':
        try:
            db.drop_db()
            print('Схема успешно удалена!')
            print('Выход из программы.')
            exit(0)
        except Exception as e:
            print('При удалении схемы базы данных возникла непредвиденная ошибка.')
            print(e)
    elif choice == '3':
        print('Пока!')
        exit(0)
    else:
        print('Не найдена опция.')
