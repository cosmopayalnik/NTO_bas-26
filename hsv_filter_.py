import cv2
import numpy as np


def nothing(x):
    pass


def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Не удалось открыть камеру")
        return

    cv2.namedWindow('HSV Settings')

    # --- Ползунки HSV ---
    cv2.createTrackbar('H Min', 'HSV Settings', 0, 179, nothing)
    cv2.createTrackbar('H Max', 'HSV Settings', 30, 179, nothing)
    cv2.createTrackbar('S Min', 'HSV Settings', 111, 255, nothing)
    cv2.createTrackbar('S Max', 'HSV Settings', 217, 255, nothing)
    cv2.createTrackbar('V Min', 'HSV Settings', 172, 255, nothing)
    cv2.createTrackbar('V Max', 'HSV Settings', 255, 255, nothing)

    # --- Ползунок площади ---
    # Максимальное значение зависит от разрешения камеры.
    # Для 640x480 полная площадь ~307200, ставим с запасом.
    cv2.createTrackbar('Min Area', 'HSV Settings', 500, 50000, nothing)

    print("Нажмите 'q' для выхода")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 1. Конвертация в HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # 2. Получение значений ползунков
        h_min = cv2.getTrackbarPos('H Min', 'HSV Settings')
        h_max = cv2.getTrackbarPos('H Max', 'HSV Settings')
        s_min = cv2.getTrackbarPos('S Min', 'HSV Settings')
        s_max = cv2.getTrackbarPos('S Max', 'HSV Settings')
        v_min = cv2.getTrackbarPos('V Min', 'HSV Settings')
        v_max = cv2.getTrackbarPos('V Max', 'HSV Settings')
        min_area = cv2.getTrackbarPos('Min Area', 'HSV Settings')

        # 3. Создание маски
        lower_bound = np.array([h_min, s_min, v_min])
        upper_bound = np.array([h_max, s_max, v_max])
        mask = cv2.inRange(hsv, lower_bound, upper_bound)

        # 4. Фильтрация по площади (поиск контуров)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Копия кадра для рисования
        result = frame.copy()
        object_detected = False

        for contour in contours:
            area = cv2.contourArea(contour)

            # Если площадь контура больше порога
            if area > min_area:
                object_detected = True
                # Получаем координаты ограничивающего прямоугольника
                x, y, w, h = cv2.boundingRect(contour)

                # Рисуем прямоугольник вокруг объекта
                cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Подписываем площадь
                cv2.putText(result, f'Area: {int(area)}', (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Статус детекции
        status = "OBJECT DETECTED" if object_detected else "NO OBJECT"
        color = (0, 255, 0) if object_detected else (0, 0, 255)
        cv2.putText(result, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        # 5. Отображение
        cv2.imshow('Original Frame', frame)
        cv2.imshow('Mask (Binary)', mask)
        cv2.imshow('Result (Filtered)', result)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()