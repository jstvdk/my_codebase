import numpy as np
import math
import sys
import matplotlib.pyplot as plt

#De moment nomes te en compte un r, cal modificar R per tal de probar diferents radis
def HoughT(x, y, z, d, w, f):
# *** HoughT retorna aquell anell que millor s'ajusta a l'anell generat pel muo, donant el centre i coordenades x-y d'aquest
# *** Variables:
#    x són les coordenades en l'eix X de l'anell del muo
#    y són les coordenades en l'eix Y de l'anell del muo
#    z és la intensitat en cada punt de l'anell del muo
#    w és el gruix de l'anell que s'ajusta
#    f és la focal utilitzada per passar de mestres a graus
    x = x.value
    y = y.value
    R_min = 0.9
    R_max = 1.4
    R = np.linspace(R_min, R_max, 50)*f/180.*np.pi
    A = np.zeros((len(x),len(R),5))

    for j in range(len(R)):
        for i in range(len(x)):
            Range_0 = np.sqrt((x - x[i]) ** 2 + (y - y[i]) ** 2)
            Range_1 = np.sqrt((x - (x[i] + d)) ** 2 + (y - y[i]) ** 2)
            Range_2 = np.sqrt((x - (x[i] - d)) ** 2 + (y - y[i]) ** 2)
            Range_3 = np.sqrt((x - x[i]) ** 2 + (y - (y[i] + d)) ** 2)
            Range_4 = np.sqrt((x - x[i]) ** 2 + (y - (y[i] - d)) ** 2)

            Q_0 = (z)[(Range_0 <= R[j]) & (Range_0 > R[j]-w)]
            Q_1 = (z)[(Range_1 <= R[j]) & (Range_1 > R[j] - w)]
            Q_2 = (z)[(Range_2 <= R[j]) & (Range_2 > R[j] - w)]
            Q_3 = (z)[(Range_3 <= R[j]) & (Range_3 > R[j] - w)]
            Q_4 = (z)[(Range_4 <= R[j]) & (Range_4 > R[j] - w)]

            A[i][j][0] = np.sum(Q_0) / len(Q_0)
            A[i][j][1] = np.sum(Q_1) / len(Q_1)
            A[i][j][2] = np.sum(Q_2) / len(Q_2)
            A[i][j][3] = np.sum(Q_3) / len(Q_3)
            A[i][j][4] = np.sum(Q_4) / len(Q_4)

    #mA = np.argmax(A)
    mA = np.unravel_index(A.argmax(), A.shape)

    if mA[2] == 0:
        mpix = np.sqrt((x - x[mA[0]]) ** 2 + (y - y[mA[0]]) ** 2)
        center_x = x[mA[0]]
        center_y = y[mA[0]]
    if mA[2] == 1:
        mpix = np.sqrt((x - (x[mA[0]] + d)) ** 2 + (y - y[mA[0]]) ** 2)
        center_x = x[mA[0]] + d
        center_y = y[mA[0]]
    if mA[2] == 2:
        mpix = np.sqrt((x - (x[mA[0]] - d)) ** 2 + (y - y[mA[0]]) ** 2)
        center_x = x[mA[0]] - d
        center_y = y[mA[0]]
    if mA[2] == 3:
        mpix = np.sqrt((x - x[mA[0]]) ** 2 + (y - (y[mA[0]] + d)) ** 2)
        center_x = x[mA[0]]
        center_y = y[mA[0]] + d
    if mA[2] == 4:
        mpix = np.sqrt((x - x[mA[0]]) ** 2 + (y - (y[mA[0]] - d)) ** 2)
        center_x = x[mA[0]]
        center_y = y[mA[0]] - d

    circle_x = x[(mpix <= R[mA[1]]) & (mpix > R[mA[1]]-w)]
    circle_y = y[(mpix <= R[mA[1]]) & (mpix > R[mA[1]]-w)]
    radius = R[mA[1]]
    return center_x, center_y, circle_x, circle_y, radius, w