import cv2
import datetime


def record_video(output_filename='drone_test_video.avi', fps=30.0):
    """
    Записывает видео с веб-камеры до нажатия клавиши 'q'
    """
    # Открываем камеру (0 - первая камера, попробуй 1 если не работает)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Не удалось открыть камеру!")
        return

    # Получаем размеры кадра
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Кодек для сохранения видео (XVID совместим с большинством плееров)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    # Создаем объект для записи
    out = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))

    print(f"✅ Запись началась! Файл: {output_filename}")
    print(f"📹 Разрешение: {width}x{height}, FPS: {fps}")
    print("⏹️ Нажми 'q' для остановки записи")
    print("-" * 50)

    start_time = datetime.datetime.now()
    frame_count = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            print("❌ Ошибка чтения кадра!")
            break

        # Записываем кадр
        out.write(frame)
        frame_count += 1

        # Считаем время записи
        current_time = datetime.datetime.now()
        duration = (current_time - start_time).total_seconds()

        # Отображаем информацию на экране
        cv2.putText(frame, f"RECORDING... {duration:.1f}s", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(frame, f"Frames: {frame_count}", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "Press 'q' to stop", (10, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Показываем превью
        cv2.imshow('Recording Video', frame)

        # Выход по клавише 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Освобождаем ресурсы
    cap.release()
    out.release()
    cv2.destroyAllWindows()

    print("-" * 50)
    print(f"✅ Запись завершена!")
    print(f"📁 Файл сохранен: {output_filename}")
    print(f"⏱️ Длительность: {duration:.1f} секунд")
    print(f"🎬 Всего кадров: {frame_count}")


if __name__ == "__main__":
    # Можешь изменить имя файла или FPS при необходимости
    record_video(output_filename='drone_gimbal_test.avi', fps=30.0)