import cv2
import numpy as np
from PIL import Image, ImageTk
import pyautogui as pg


# диапозон цвета маркера танка [190, 0, 220] [255, 25, 255]
# lower_color = np.array([100, 0, 190], dtype=np.uint8)
# upper_color = np.array([255, 120, 255], dtype=np.uint8)
# [0, 100, 200], [100, 255, 255] рамки оранжевого цвета

def getFiltredImage(ImagePath:str, isWindowsOpen:bool, Lower_color, Upper_color):  
    if ImagePath == 'screen': 
        image = cv2.imread('./img/screenshot.png')
    else:
        image = cv2.imread(ImagePath)

    lower_color = np.array(Lower_color, dtype=np.uint8)
    upper_color = np.array(Upper_color, dtype=np.uint8)

    color_mask = cv2.inRange(image, lower_color, upper_color)
    result = cv2.bitwise_and(image, image, mask=color_mask)

    pixelPos = np.column_stack(np.where(color_mask > 0))

    if isWindowsOpen:
        # Отображение результатов
        cv2.imshow('Original Image', image)
        cv2.imshow('Filtered Image', result)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return pixelPos
    else:
        return pixelPos

def find_similar_arrays(target_array, array_of_arrays, max_difference):
    result_arrays = []

    for arr in array_of_arrays:
        if all(abs(a - b) <= max_difference for a, b in zip(target_array, arr)):
            result_arrays.append(arr)

    return result_arrays

def getCenter(list):
    # поиск центра очка
    allX = []
    allY = []
    for i in list:
        allX.append(i[0])
        allY.append(i[1])
    maxX = max(allX)
    maxY = max(allY)
    minX = min(allX)
    minY = min(allY)

    centerPos = [round((maxX+minX)/2), round((maxY+minY)/2)]
    return centerPos

def are_arrays_equal(arr1Full, arr2Full, max_equal):
    # Проверяем, одинаковы ли массивы
    arr1 = [arr1Full[0], arr1Full[1]]
    arr2 = [arr2Full[0], arr2Full[1]]
    equal_arrays = np.array_equal(arr1, arr2)

    if equal_arrays:
        return True
    
    # Проверяем, есть ли максимальное отличие чисел не более 3
    max_difference = np.max(np.abs(np.array(arr1) - np.array(arr2)))
    
    return max_difference <= max_equal

def is_in_range(num1, num2, rangge):
    return num2 - 5 <= num1 <= num2 + rangge

def scale_img(path, outputImgName, width):
    # Загрузка изображения
    image_path = path
    img = Image.open(image_path)

    # Изменение размера изображения
    resized_img = img.resize((width, width))

    # Сохранение измененного изображения (если нужно)
    newImgPath = "./img/"+outputImgName+".png"
    resized_img.save(newImgPath)
    return newImgPath

# print(pixels)

# getTankDirection(pixels)

pon = getFiltredImage('screen', True,  [200, 0, 0],  [255, 50, 255]) #BRG
print(len(pon))

# pg.sleep(3)
# pos = pg.position()
# print(pg.pixel(pos.x, pos.y))
























