# импорт библиотек
import pandas as pd
from pioneer_sdk import Pioneer
import time
import math


def get_attitude(drone):  # ф-ция получения координат
    if 'ATTITUDE' in drone.msg_archive:
        msg_dict = drone.msg_archive['ATTITUDE']
        msg = msg_dict['msg']
        if not msg_dict['is_read'].is_set():
            msg_dict['is_read'].set()
            return msg.roll, msg.pitch, msg.yaw  # получаем значения крена, тангажа и рысканья
    return None


def main():
    drone = Pioneer()
    roll_data = []  # массив с значением крена
    pitch_data = []  # массив с значением тангажа
    yaw_data = []  # массив с значением рысканья

    try:
        while True:
            angles = get_attitude(drone)
            if angles:

                roll, pitch, yaw = angles  # получаем значения крена, тангажа и рысканья
                global_yaw = math.degrees(yaw)

                # Добавляем данные
                roll_data.append(math.degrees(roll))
                pitch_data.append(math.degrees(pitch))
                yaw_data.append(math.degrees(yaw))

                # выводим данные в консоль
                print(f"Крен (roll): {math.degrees(roll):.2f}° | Тангаж (pitch): {math.degrees(pitch):.2f}° | Рысканье (yaw): {global_yaw:.2f}")
            else:
                print("Нет данных о ориентации")

            time.sleep(0.5)

    except KeyboardInterrupt:
        roll_list = []
        pitch_list = []
        yaw_list = []
        for i in range(0, len(roll_data) // 5):
            roll_list.append(sum(roll_data[i * 5:i * 5 + 5]) / 5)
            pitch_list.append(sum(pitch_data[i * 5:i * 5 + 5]) / 5)
            yaw_list.append(sum(yaw_data[i * 5:i * 5 + 5]) / 5)

        # Сохраняем данные в Excel
        df = pd.DataFrame({
            'номер измерения': range(1, len(roll_list) + 1),
            'тангаж_тм': roll_list,
            'крен_тм': pitch_list,
            'рысканье_тм': yaw_list
        })

        # Записываем в Excel
        df.to_excel('C:/Users/User/PycharmProjects/pioneer/drone_data.xlsx', index=False)
        print("Данные успешно сохранены в Excel.")


if __name__ == "__main__":
    main()