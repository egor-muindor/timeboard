import json
import time

from timeboard import Timeboard

all_timeboads = []
error_timeboards = []
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
        except:
            if c < 3:
                c += 1
                print('Расписание группы %s не удалось скачать' % group_id)
                time.sleep(5)
            else:
                success = True
                print('Расписание группы %s пропущено' % group_id)

f = open("data.json", "w")
f.write(json.dumps(all_timeboads))
f.close()
