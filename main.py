import pyautogui as pg
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
import keyboard as kb
import asyncio
import math
from cv2defs import getFiltredImage, are_arrays_equal, scale_img, is_in_range
from autopilot import getAtan2

# (189, 45, 145) (185, 42, 142) (188, 44, 144) (189, 46, 146) (183, 46, 141) (195, 49, 150) (196, 50, 151) (184, 41, 140)

# player color = (220, 250, 253)
# top lef minimap = 0, 825
# right bottom minimap = 200, 1025

p = 1.219 #количество пикселей занимающих 1 пиксель в minimap.img
mapPath = './img/new-bey-way.png'
isAutopilot = False
currentDeg = 0 
rotateSpeed = 32.7  # градусы в секунду
# rotateSpeed = 72.05
player_color1 = [150, 0, 0]
player_color2 = [255, 50, 50]
autopilotPath = []
letterNum = 1

pathWindow = None
window = None

# Главное окно
def createMainWin():
    global window
    window = tk.Tk()
    window.title("поне")
    window.geometry("400x120+250+0")
    window.attributes('-topmost', 1)

    # pixCountText = tk.Label(window, text="pixel count:\n0", font=("Arial", 10), bg='yellow')
    # pixCountText.place(x=0, y=0, width=100, height=53)
    autopilotText = tk.Label(window, text="autopilot: off", font=("Arial", 10), bg='lightpink')
    autopilotText.place(x=0, y=55, width=400, height=35)
    isTankText = tk.Label(window, text="tank: fined", font=("Arial", 10), bg='lightgreen')
    isTankText.place(x=0, y=90, width=400, height=30)
    
    return autopilotText, isTankText

isTankText, autopilotText = createMainWin()


# определение направления танка
def getTankDirection2(e):

    # tankAng = 0 # градусы поворота танка | влево от 0 до 180 | вправо от 0 до -180

    def rotateTank(direction, deg):
        sec = deg / rotateSpeed
        if direction == 'left':
            kb.press('a')
            pg.sleep(sec)
            kb.release('a')
        elif direction == 'right':
            kb.press('d')
            pg.sleep(sec)
            kb.release('d')

    def rotate1(tankPos, targetPos, tankDeg):
        angle = normalTankAngle(tankPos, targetPos)

        if angle <= 0:
            if tankDeg > angle and tankDeg <= 0:
                deg = angle*-1 - tankDeg*-1
                # поворот влево
                if deg>180:
                    rotateTank('right', 360-deg)
                else:
                    rotateTank('left', deg)
            elif tankDeg < angle and tankDeg <= 0:
                deg = tankDeg*-1 - angle*-1
                # поворот вправо
                if deg>180:
                    rotateTank('right', 360-deg)
                else:
                    rotateTank('right', deg)
                
            else:
                deg = tankDeg + angle*-1
                # поворот влево
                if deg>180:
                    rotateTank('right', 360-deg)
                else:
                    rotateTank('left', deg)
                # rotateTank('left', deg)

        elif angle > 0:
            if tankDeg > angle and tankDeg > 0:
                deg = tankDeg - angle
                # поворот влево
                if deg>180:
                    rotateTank('right', 360-deg)
                else:
                    rotateTank('left', deg)
                # rotateTank('left', deg)
            elif tankDeg < angle and tankDeg > 0:
                deg = angle - tankDeg
                # поворот вправо
                if deg>180:
                    rotateTank('left', 360-deg)
                else:
                    rotateTank('right', deg)
                # rotateTank('right', deg)
            else:
                deg = tankDeg*-1 + angle
                # поворот вправо
                if deg>180:
                    rotateTank('left', 360-deg)
                else:
                    rotateTank('right', deg)
                # rotateTank('right', deg) #aboba

    def normalTankAngle(pos1, pos2):
        tankDeg = getAtan2(pos1, pos2)
        if tankDeg<0:
            tankDeg = tankDeg*-1

        if pos1[0] <= pos2[0] and pos1[1] <= pos2[1]:
            # 180 - deg влево
            tankAng = (180-tankDeg)*-1

        elif pos1[0] >= pos2[0] and pos1[1] >= pos2[1]:
            # 180 - deg вправо
            tankAng = 180-tankDeg
        
        elif pos1[0] <= pos2[0] and pos1[1] >= pos2[1]:
            # 180 - deg вправо
            tankAng = 180-tankDeg
        
        elif pos1[0] >= pos2[0] and pos1[1] <= pos2[1]:
            # 180 - deg влево
            tankAng = (180-tankDeg)*-1

        '''
            функция возвращает угол между прямой направления танка и положительной осью OX 
            от 0 до 180 или от 0 до -180
            если угол отрицательный значит танк повернут влево
            если угол положительный значит танк повернут вправо
        '''

        return tankAng

    async def minimapMarker(pos1):
        pos = [pos1[1]*2, pos1[0]*2]

        tankMarker.place_forget()
        tankMarker.place(x=pos[0]-5, y=pos[1]-5, width=10, height=10)
        tankMarkerText.place_forget()
        tankMarkerText.config(text='x: '+str(round(pos[1]))+' | y: '+str(round(pos[0])))
        tankMarkerText.place(x=pos[0], y=pos[1]-20, width=115, height=20)

        point = autopilotPath[pointPassed]
        pointsLabel.config(text="points: "+str(len(autopilotPath)))
        progressLabel.config(text="passed: "+str(pointPassed))
        targetNameLabel.config(text="point: "+str(point[2]))
        targetPosLabel.config(text="pos{ x: "+str(point[1])+" | y: "+str(point[0])+"}")

        def draw_empty_circle(canvas, x, y, radius, border_width):
            canvas.create_oval(x - radius, y - radius, x + radius, y + radius, outline="green", width=border_width, tags='oval1')
        
        canvas.delete('oval1')
        draw_empty_circle(canvas, pos[0], pos[1], 40, 2)


    def main(target, rotateI):
        finish = False
        pos = []
        i = 3
        while finish == False:

            # нахождение координат танка
            pg.screenshot('./img/screenshot.png', region=(0, 825, 200, 200))
            tankPos = getTankPos(False)
            pos = tankPos

            isPoint = are_arrays_equal(tankPos, target, 5)
            if isPoint:
                kb.release('w')
                return

            if i == rotateI:
                i = 0
                kb.release('w')
                # получение координт двух крайних точек направления танка
                points = getTankDirPos(False)
                # получение угла между прямой направления танка и положительной осью OX
                tankDirAngle = normalTankAngle(points[0], points[1])
                # получение угла между танком и целью и поворот
                rotate1(tankPos, target, tankDirAngle)

            kb.press('w')
            pg.sleep(1)
            i += 1
            


    pointPassed = 0
    for path in autopilotPath:
        print('начато движение')
        main(path, 5)
        # del autopilotPath[pointPassed]
        pointPassed += 1
        if pointPassed >= len(autopilotPath):
            break
    else:
        return

    # если до цели далеко танк едет по прямой, если близко танк останавливается


def createPathInfoWin():
    # points list | progress | target | 

    global pointsLabel
    global progressLabel
    global targetNameLabel
    global targetPosLabel

    pathInfoWin = tk.Toplevel(window)
    pathInfoWin.title("Point")
    pathInfoWin.geometry("300x100+250+250")
    pathInfoWin.attributes('-topmost', 1)

    pointsLabel = tk.Label(pathInfoWin, text="points: 0", font=("Arial", 10), bg='lightgreen')
    pointsLabel.place(x=0, y=0, width=150, height=30)

    progressLabel = tk.Label(pathInfoWin, text="passed: 0", font=("Arial", 10), bg='green')
    progressLabel.place(x=150, y=0, width=150, height=30)

    targetNameLabel = tk.Label(pathInfoWin, text="point: N", font=("Arial", 10), bg='yellow')
    targetNameLabel.place(x=0, y=30, width=100, height=30)
    
    targetPosLabel = tk.Label(pathInfoWin, text="pos{ x: none | y: none}", font=("Arial", 10), bg='lightyellow')
    targetPosLabel.place(x=100, y=30, width=200, height=30)

# создание окна навигации
def createPathWindow(e):
    if e.event_type != kb.KEY_UP:
        return
    
    global letterNum
    global photo
    global tankMarker
    global tankMarkerText
    global canvas
    letterNum = 1
    img_width=400
    # print(autopilotPath)

    def draw_point(x, y, text, width):
        text = tk.Label(pathWindow, text=text, font=("Arial", 9), bg='green', fg='white')
        text.place(x=x-width/2, y=y-width/2, width=width, height=width)

    def on_click(event):
        global letterNum
        x = event.x
        y = event.y
        letter = chr(ord('A') + letterNum - 1)
        letterNum += 1
        draw_point(x, y, letter, 15)
        autopilotPath.append([round(y/2), round(x/2), letter])
        print(autopilotPath)
    
    pathWindow = tk.Toplevel(window)
    pathWindow.title("navigation")
    pathWindow.geometry(str(img_width)+"x"+str(img_width)+"+250+250")
    pathWindow.attributes('-topmost', 1)

    image_path = "./img/screenshot.png"
    new_img_path = scale_img(image_path, 'scaled-screenshot', img_width)
    image = Image.open(new_img_path)
    photo = ImageTk.PhotoImage(image)

    canvas = Canvas(pathWindow)
    canvas.place(x=0, y=0, width=img_width, height=img_width)
    canvas.create_image(0,0,anchor=NW,image=photo)
    
    tankMarker = tk.Label(pathWindow, text="T", font=("Arial", 10, 'bold'), bg='blue')
    tankMarker.place(x=100, y=100, width=10, height=10)
    tankMarkerText = tk.Label(pathWindow, text="x: 0 | y: 0", font=("Arial", 10), bg='lightyellow')
    tankMarkerText.place(x=100, y=110, width=100, height=20)


    pathWindow.bind("<Button-1>", on_click)
    createPathInfoWin()

# получение позиции танка
def getTankPos(isScreenshot):
    if isScreenshot:
        pg.screenshot('./img/screenshot.png', region=(0, 825, 200, 200))
    pixels = getFiltredImage('screen', False, player_color1, player_color2)

    if len(pixels)==0:
        print('eror: pixels not found!')
        return False
    
    pos = pixels[0]
    minimapPos = [pos[0], pos[1]]
    # функция возвращает положение танка на миникарте стороной 200px
    return minimapPos

# получение крайних точек направления танка
def getTankDirPos(isScreenshot):
    if isScreenshot:
        pg.screenshot('./img/screenshot.png', region=(0, 825, 200, 200))
    pixels = getFiltredImage('screen', False, [150, 0, 150], [255, 100, 255])

    if len(pixels)<1:
        print("eror: pixels not found!")
        return False
    
    points = []

    xAll = []
    yAll = []
    for i in pixels:
        xAll.append(i[0])
        yAll.append(i[1])

    minX = min(xAll)
    maxX = max(xAll)
    minXcount = xAll.count(minX)
    maxXcount = xAll.count(maxX)

    if minXcount > 10 or maxXcount > 10:
        minY = min(yAll)
        maxY = max(yAll)
        points = [[xAll[yAll.index(minY)], minY], [xAll[yAll.index(maxY)], maxY]]
    else:
        points = [[minX, yAll[xAll.index(minX)]], [maxX, yAll[xAll.index(maxX)]]]

    return points


def mainDef(e):
    if e.event_type != kb.KEY_UP:
        return
    
    pg.screenshot('./img/screenshot.png', region=(0, 825, 200, 200))


kb.hook_key('print_screen', mainDef)
kb.hook_key('f6', getTankDirection2)
kb.hook_key('f7', createPathWindow)
window.mainloop()


'''
способ с поворотом камеры:

0. дважды нажимается шифт

1. функция getDirPoints() определяются 2 крайние точки луча
    1. находится ближайшая точка луча к танку
    2. функция возвращает [[начало луча], [конец луча]]

2. функция tankDir()
    1. принимает [[начало луча], [конец луча]]
    2. возвращает угол между лучем и целью

3. функция rotateCam()
    1. принимает угол
    2. поворачивает камеру так чтобы луч проходил через цель

4. функция хз() определяет правильно ли повернута камера
    1. getDirPoints() получает массив с точКАМи луча
    2. проверка: есть ли координаты цели в массиве координат луча
        * если луч проходит через цель: пункт 5
        * иначе все по новой

5. функция move()
    1. цикл с итерацией раз в 1 сек
    2. каждую итерацию проверка достиг ли танк цели
    3. танк у цели? да: все по новой | нет: ТЫ РАК


'''


