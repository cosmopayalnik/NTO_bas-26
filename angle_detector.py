import cv2
import numpy as np
import math


def nothing(x):
    pass


def calculate_angle(box, rect):
    """
    Более надежное вычисление угла с использованием данных из minAreaRect
    """
    (center), (width, height), angle_rect = rect

    # В OpenCV 4.5.4+ угол возвращается в диапазоне [0, 90]
    # В более старых версиях в диапазоне [-90, 0)

    # Определяем ориентацию прямоугольника
    if width < height:
        # Прямоугольник "стоит" вертикально
        # Угол нужно скорректировать
        angle = angle_rect - 90
    else:
        # Прямоугольник "лежит" горизонтально
        angle = angle_rect

    # Нормализуем к диапазону [-90, 90]
    while angle > 90:
        angle -= 180
    while angle < -90:
        angle += 180

    return angle


def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Не удалось открыть камеру")
        return

    cv2.namedWindow('HSV Settings')

    # --- Ползунки HSV с дефолтными значениями ---
    # H Min: 0
    cv2.createTrackbar('H Min', 'HSV Settings', 0, 179, nothing)
    # H Max: 30
    cv2.createTrackbar('H Max', 'HSV Settings', 18, 179, nothing)
    # S Min: 111
    cv2.createTrackbar('S Min', 'HSV Settings', 97, 255, nothing)
    # S Max: 217
    cv2.createTrackbar('S Max', 'HSV Settings', 199, 255, nothing)
    # V Min: 172
    cv2.createTrackbar('V Min', 'HSV Settings', 172, 255, nothing)
    # V Max: 255
    cv2.createTrackbar('V Max', 'HSV Settings', 255, 255, nothing)

    # --- Ползунок площади ---
    # Min Area: 0
    cv2.createTrackbar('Min Area', 'HSV Settings', 0, 50000, nothing)

    print("Нажмите 'q' для выхода")
    print("Дефолтные значения HSV установлены для детекции красного/оранжевого цвета")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Получение значений
        h_min = cv2.getTrackbarPos('H Min', 'HSV Settings')
        h_max = cv2.getTrackbarPos('H Max', 'HSV Settings')
        s_min = cv2.getTrackbarPos('S Min', 'HSV Settings')
        s_max = cv2.getTrackbarPos('S Max', 'HSV Settings')
        v_min = cv2.getTrackbarPos('V Min', 'HSV Settings')
        v_max = cv2.getTrackbarPos('V Max', 'HSV Settings')
        min_area = cv2.getTrackbarPos('Min Area', 'HSV Settings')

        lower_bound = np.array([h_min, s_min, v_min])
        upper_bound = np.array([h_max, s_max, v_max])
        mask = cv2.inRange(hsv, lower_bound, upper_bound)

        # Морфологические операции для очистки шума
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        result = frame.copy()
        largest_contour = None
        max_contour_area = 0

        # 1. Сначала найдем самый большой подходящий контур
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > min_area and area > max_contour_area:
                max_contour_area = area
                largest_contour = contour

        angle_text = "No Object"
        color_text = (0, 0, 255)  # Красный по умолчанию

        if largest_contour is not None:
            # 2. Получаем поворачивающийся прямоугольник
            rect = cv2.minAreaRect(largest_contour)
            (center), (width, height), angle_rect = rect

            # 3. Получаем 4 вершины прямоугольника
            box = cv2.boxPoints(rect)
            box = box.astype(np.int32)

            # 4. Рисуем контур прямоугольника
            cv2.drawContours(result, [box], 0, (0, 255, 0), 2)

            # 5. Рисуем центр
            cv2.circle(result, (int(center[0]), int(center[1])), 5, (255, 0, 0), -1)

            # 6. Вычисляем угол наклона относительно горизонта
            angle = calculate_angle(box, rect)

            # Нормализуем угол
            if angle > 90:
                angle -= 180
            elif angle < -90:
                angle += 180

            angle_text = f"Angle: {angle:.1f} deg"
            color_text = (0, 255, 0)  # Зеленый, если объект найден

            # Вывод текста с углом
            cv2.putText(result, angle_text, (int(center[0]) - 50, int(center[1]) - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Вывод площади
            cv2.putText(result, f'Area: {int(max_contour_area)}', (int(center[0]) - 50, int(center[1]) + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Статус детекции в углу
        cv2.putText(result, "DETECTED" if largest_contour is not None else "SEARCHING",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color_text, 2)

        cv2.imshow('Original Frame', frame)
        cv2.imshow('Mask (Binary)', mask)
        cv2.imshow('Result (Angle)', result)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()