
import cv2
import numpy as np
import video
import serial
import time

arduino = serial.Serial('COM4', 9600)
time.sleep(2)  
print("Initialized")


directions = {
    1: "Left Back",
    2: "Backward",
    3: "Backward Right",
    4: "Left",
    5: "Stay Still",
    6: "Right",
    7: "Forward Left",
    8: "Forward",
}

def send_direction(direction):
    print("Direction:", directions[direction])
    arduino.write(bytes([direction]))

if __name__ == '__main__':
    cv2.namedWindow("result")

    cap = video.create_capture(0)

    # Диапазоны 
    red_hsv_min = np.array((0, 116, 205), np.uint8)
    red_hsv_max = np.array((10, 255, 255), np.uint8)
    green_hsv_min = np.array((40, 100, 100), np.uint8)
    green_hsv_max = np.array((80, 255, 255), np.uint8)

    color_green = (0, 255, 0)
    color_yellow = (0, 255, 255)
    color_red = (0, 0, 255)

    
    state = 'approach_red'  
    red_taken = False
    green_taken = False

    while True:
        flag, img = cap.read()
        img = cv2.flip(img, 1)  

        # Обработка красного объекта
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        thresh_red = cv2.inRange(hsv, red_hsv_min, red_hsv_max)
        thresh_green = cv2.inRange(hsv, green_hsv_min, green_hsv_max)

        contours_red, _ = cv2.findContours(thresh_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours_green, _ = cv2.findContours(thresh_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if state == 'approach_red':
            while not contours_red:
                out = 6
            if contours_red:
                largest_contour = max(contours_red, key=cv2.contourArea)
                moments = cv2.moments(largest_contour)
                dArea = moments['m00']

                if dArea > 100:
                    x_coords = largest_contour[:, 0, 0]
                    x_min, x_max = x_coords.min(), x_coords.max()

                    
                    x_center = int((x_min + x_max) / 2)

                    
                    if x_center > 320 + 31:
                        out = 6  # Вправо
                    elif x_center < 320 - 31:
                        out = 4  # Влево
                    else:
                        out = 8  # Вперед

                    
                    if x_max - x_min >= 250:
                        out = 5
                        time.sleep(10)
                        out = 10
                        red_taken = True
                        state = 'return_to_start'  

                send_direction(out)
        # Обработка зеленого объекта
        elif state == 'return_to_start':
            
            out = 2  # Назад
            #уже на трасе посмотрим
            if red_taken:
                state = 'approach_green'  
            send_direction(out)

        elif state == 'approach_green':
            while not contours_green:
                out = 6
            if contours_green:
                largest_contour = max(contours_green, key=cv2.contourArea)
                moments = cv2.moments(largest_contour)
                dArea = moments['m00']

                if dArea > 100:
                    x_coords = largest_contour[:, 0, 0]
                    x_min, x_max = x_coords.min(), x_coords.max()

                    
                    x_center = int((x_min + x_max) / 2)
                    
                    if x_center > 320 + 31:
                        out = 6  # Вправо
                    elif x_center < 320 - 31:
                        out = 4  # Влево
                    else:
                        out = 8  # Вперед

                    
                    if x_max - x_min >= 250:
                        out = 5
                        time.sleep(10)
                        out = 10
                        green_taken = True
                        state = 'return_to_start_green'  

                send_direction(out)

        elif state == 'return_to_start_green':
            
            out = 2  # Назад
            #уже на трасе посмотрим
            if green_taken:  
                
                
                state = 'finished'  

            send_direction(out)

        cv2.imshow('result', img)
        cv2.imshow('red', thresh_red)
        cv2.imshow('green', thresh_green)

        ch = cv2.waitKey(5)
        if ch == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
