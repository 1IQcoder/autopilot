import math

rotateSpeed = 35.48  # градусы в секунду


def getAtan2(tankPos, targetPos):

    # Нахождение вектора между точками
    v_x = tankPos[0] - targetPos[0]
    v_y = tankPos[1] - targetPos[1]

    # Нахождение угла между вектором и осью x
    angle_rad = math.atan2(v_y, v_x)

    # Преобразование угла из радиан в градусы
    angle_deg = round(math.degrees(angle_rad))
    # print("угол: "+str(angle_deg))
    return angle_deg


# print(rotateToPoint([5, 5], [3, 9]))





















