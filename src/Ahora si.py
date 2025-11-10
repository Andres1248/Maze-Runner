'''
Referencias:
https://docs.python.org/3/library/csv.html
https://www.youtube.com/watch?v=Xi52tx6phRU&t=305s
https://docs.python.org/3/library/random.html#functions-for-sequences
https://www.pygame.org/docs/ref/image.html#module-pygame.image
https://www.pygame.org/docs/ref/key.html#module-pygame.key

'''

import time
import random
import csv
import os
import pygame
from pygame import FULLSCREEN
import sys
import sqlite3


nivel1=True
nivel2=True
nivel3=True
nivel4=True


puntosP=0
puntosY=0
sys.setrecursionlimit(10000)
tiempo_ultimo_movimiento_bicho = time.time()
delay_movimiento_bicho = 0.5

tiempo_congelado = None  # No está congelado al inicio
jugador_congelado = False
duracion_congelado = 5


modo = ''
while modo.lower()!='automatic' and modo.lower()!='adventure' and modo.lower()!='competition':
    modo = input('Which mode would you like to play (automatic/adventure/competition): ')




ambiente = ''
while ambiente.lower()!='ice' and ambiente.lower()!='fire' and ambiente.lower()!='space':
    ambiente = input('In which environment would you like to play (Space/Fire/Ice)? ')


def esta_tocando(Prow, Pcolumn, Brow, Bcolumn):
    # Devuelve True si el bicho está justo al lado o encima del jugador
    # Esto incluye las 4 direcciones principales (arriba, abajo, izquierda, derecha)
    dist_fila = abs(Prow - Brow)
    dist_col = abs(Pcolumn - Bcolumn)

    # Tocando si están en la misma posición o en posiciones adyacentes
    if (dist_fila == 0 and dist_col == 0):
        return True  # Mismo lugar
    if (dist_fila == 1 and dist_col == 0):
        return True  # Arriba o abajo
    if (dist_fila == 0 and dist_col == 1):
        return True  # Izquierda o derecha

    return False




def Automatico(laberinto, x, y, xm, ym, inversa, pasos):
    if x == xm and y == ym:
        laberinto[x][y] = 'F'
        return laberinto, pasos

    disponibles = []

    # Arriba (N)
    if y > 0 and laberinto[x][y - 1] == True:
        disponibles.append('N')

    # Abajo (S)
    if y < len(laberinto[0]) - 1 and laberinto[x][y + 1] == True:
        disponibles.append('S')

    # Derecha (E)
    if x < len(laberinto) - 1 and laberinto[x + 1][y] == True:
        disponibles.append('E')

    # Izquierda (O)
    if x > 0 and laberinto[x - 1][y] == True:
        disponibles.append('O')

    if disponibles == []:
        if inversa == []:
            return False, pasos  # No hay más caminos para intentar
        else:
            turn_back = inversa.pop()
            laberinto[x][y] = 'V'
            if turn_back == 'N':
                return Automatico(laberinto, x, y - 1, xm, ym, inversa, pasos+1)
            elif turn_back == 'S':
                return Automatico(laberinto, x, y + 1, xm, ym, inversa, pasos+1)
            elif turn_back == 'E':
                return Automatico(laberinto, x + 1, y, xm, ym, inversa, pasos+1)
            elif turn_back == 'O':
                return Automatico(laberinto, x - 1, y, xm, ym, inversa, pasos+1)
    else:
        direccion = random.choice(disponibles)
        laberinto[x][y] = 'V'
        if direccion == 'N':
            return Automatico(laberinto, x, y - 1, xm, ym, inversa + ['S'], pasos + 1)
        elif direccion == 'S':
            return Automatico(laberinto, x, y + 1, xm, ym, inversa + ['N'], pasos + 1)
        elif direccion == 'E':
            return Automatico(laberinto, x + 1, y, xm, ym, inversa + ['O'], pasos + 1)
        elif direccion == 'O':
            return Automatico(laberinto, x - 1, y, xm, ym, inversa + ['E'], pasos + 1)





def ruta(x, y, xm, ym, laberinto, visitado=None):
    if visitado is None:
        visitado = [[False for _ in fila] for fila in laberinto]

    # Fuera de límites o en celda no transitable o ya visitada
    if not (0 <= x < len(laberinto[0]) and 0 <= y < len(laberinto)):
        return False
    if not laberinto[y][x] or visitado[y][x]:
        return False

    # Si llegamos a la posición destino, devolvemos una lista vacía como base
    if (x, y) == (xm, ym):
        return []

    visitado[y][x] = True  # Marcamos la celda actual como visitada

    # Movimientos posibles: E (Este), S (Sur), O (Oeste), N (Norte)
    movimientos = [
        ('E', 1, 0),  # Este: mover a la derecha
        ('S', 0, 1),  # Sur: mover hacia abajo
        ('O', -1, 0),  # Oeste: mover a la izquierda
        ('N', 0, -1)  # Norte: mover hacia arriba
    ]

    # Probar cada dirección
    for direccion, dx, dy in movimientos:
        nx, ny = x + dx, y + dy
        subruta = ruta(nx, ny, xm, ym, laberinto, visitado)

        if subruta is not False:
            return [direccion] + subruta  # Si encontramos una ruta, la devolvemos

    return False  # Si no hay ruta, devolvemos False




#Movemos el monstruo que mata, con la última coordenada de la función ruta. Modo aventura.
def moverVerdeAventura(Gcolumn, Grow, Pcolumn, Prow, laberinto):
    lista = ruta(Gcolumn, Grow, Pcolumn, Prow, laberinto)
    if lista[-1] == 'S':
        if Grow + 1 < rows:
            if laberinto[Grow + 1][Gcolumn] == True or laberinto[Grow][Gcolumn-1] == "IP":
                laberinto[Grow + 1][Gcolumn] = 'G'
                laberinto[Grow][Gcolumn] = True
                Grow += 1
                return laberinto
            elif laberinto[Grow + 1][Gcolumn] == 'P':
                print('¡Perdiste!')
                pygame.quit()
                exit()
            else:
                return laberinto
        else:
            return laberinto
    elif lista[-1] == 'N':
        if Grow - 1 > 0:
            if laberinto[Grow - 1][Gcolumn] == True or laberinto[Grow][Gcolumn-1] == "IP":
                laberinto[Grow - 1][Gcolumn] = 'G'
                laberinto[Grow][Gcolumn] = True
                Grow += 1
                return laberinto
            elif laberinto[Grow - 1][Gcolumn] == 'P' or ((Grow - 1 >= 0 and laberinto[Grow - 1][Gcolumn] == 'P') or
    (Grow + 1 < len(laberinto) and laberinto[Grow + 1][Gcolumn] == 'P') or
    (Gcolumn - 1 >= 0 and laberinto[Grow][Gcolumn - 1] == 'P') or
    (Gcolumn + 1 < len(laberinto[0]) and laberinto[Grow][Gcolumn + 1] == 'P')):
                print('¡Perdiste!')
                pygame.quit()
                exit()
            else:
                return laberinto
        else:
            return laberinto
    elif lista[-1] == 'O':
        if Gcolumn - 1 >= 0:
            if laberinto[Grow][Gcolumn-1] == True or laberinto[Grow][Gcolumn-1] == 'IP':
                laberinto[Grow][Gcolumn-1] = 'G'
                laberinto[Grow][Gcolumn] = True
                Gcolumn -= 1
                return laberinto
            elif laberinto[Grow][Gcolumn-1] == 'P':
                print('¡Perdiste!')
                pygame.quit()
            else:
                return laberinto
        else:
            return laberinto
    elif lista[-1] == 'E':
        if Gcolumn + 1 < cols:
            if laberinto[Grow][Gcolumn + 1] == True or laberinto[Grow][Gcolumn + 1] == 'IP':
                laberinto[Grow][Gcolumn+1] = 'G'
                laberinto[Grow][Gcolumn] = True
                Gcolumn += 1
                return laberinto
            elif laberinto[Grow][Gcolumn+1] == 'P':
                print('¡Perdiste!')
                pygame.quit()
            else:
                return laberinto
        else:
            return laberinto
    else:
        return laberinto

def moverAzulAventura(Bcolumn, Brow, laberinto, jugador_congelado):
    direcciones = []
    if Brow + 1 < rows and (laberinto[Brow + 1][Bcolumn] == True or laberinto[Brow + 1][Bcolumn] == 'P'):
        direcciones.append('S')
    if Brow - 1 >= 0 and (laberinto[Brow - 1][Bcolumn] == True or laberinto[Brow - 1][Bcolumn] == 'P'):
        direcciones.append('N')
    if Bcolumn - 1 >= 0 and (laberinto[Brow][Bcolumn - 1] == True or laberinto[Brow][Bcolumn - 1] == 'P'):
        direcciones.append('O')
    if Bcolumn + 1 < cols and (laberinto[Brow][Bcolumn + 1] == True or laberinto[Brow][Bcolumn + 1] == 'P'):
        direcciones.append('E')

    if not direcciones:
        return laberinto, 0, jugador_congelado  # No se puede mover

    direccion = random.choice(direcciones)

    if direccion == 'S':
        if laberinto[Brow + 1][Bcolumn] == 'P' and not jugador_congelado:
            laberinto[Brow + 1][Bcolumn] = 'C'
            tiempo_congelado = time.time()
            jugador_congelado = True
            return laberinto, tiempo_congelado, jugador_congelado
        else:
            laberinto[Brow + 1][Bcolumn] = 'B'
            laberinto[Brow][Bcolumn] = True
            Brow += 1

    elif direccion == 'N':
        if laberinto[Brow - 1][Bcolumn] == 'P' and not jugador_congelado:
            laberinto[Brow - 1][Bcolumn] = 'C'
            tiempo_congelado = time.time()
            jugador_congelado = True
            return laberinto, tiempo_congelado, jugador_congelado
        else:
            laberinto[Brow - 1][Bcolumn] = 'B'
            laberinto[Brow][Bcolumn] = True
            Brow -= 1

    elif direccion == 'O':
        if laberinto[Brow][Bcolumn - 1] == 'P' and not jugador_congelado:
            laberinto[Brow][Bcolumn - 1] = 'C'
            tiempo_congelado = time.time()
            jugador_congelado = True
            return laberinto, tiempo_congelado, jugador_congelado
        else:
            laberinto[Brow][Bcolumn - 1] = 'B'
            laberinto[Brow][Bcolumn] = True
            Bcolumn -= 1

    elif direccion == 'E':
        if laberinto[Brow][Bcolumn + 1] == 'P' and not jugador_congelado:
            laberinto[Brow][Bcolumn + 1] = 'C'
            tiempo_congelado = time.time()
            jugador_congelado = True
            return laberinto, tiempo_congelado, jugador_congelado
        else:
            laberinto[Brow][Bcolumn + 1] = 'B'
            laberinto[Brow][Bcolumn] = True
            Bcolumn += 1

    return laberinto, 0, jugador_congelado






#Movemos el monstruo que mata, con la última coordenada de la función ruta. Modo competición.
def moverVerdeCompeticion(Gcolumn, Grow, Pcolumn, Prow, laberinto):
    if (Grow + 1 < rows and (laberinto[Grow + 1][Gcolumn] == 'P' or laberinto[Grow + 1][Gcolumn] == 'Y')):
        laberinto[Grow + 1][Gcolumn] = 'G'
        laberinto[Grow][Gcolumn] = True
        return laberinto
    elif (Grow - 1 >= 0 and (laberinto[Grow - 1][Gcolumn] == 'P' or laberinto[Grow - 1][Gcolumn] == 'Y')):
        laberinto[Grow - 1][Gcolumn] = 'G'
        laberinto[Grow][Gcolumn] = True
        return laberinto
    elif (Gcolumn + 1 < cols and (laberinto[Grow][Gcolumn + 1] == 'P' or laberinto[Grow][Gcolumn + 1] == 'Y')):
        laberinto[Grow][Gcolumn + 1] = 'G'
        laberinto[Grow][Gcolumn] = True
        return laberinto
    elif (Gcolumn - 1 >= 0 and (laberinto[Grow][Gcolumn - 1] == 'P' or laberinto[Grow][Gcolumn - 1] == 'Y')):
        laberinto[Grow][Gcolumn - 1] = 'G'
        laberinto[Grow][Gcolumn] = True
        return laberinto
    lista = ruta(Gcolumn, Grow, Pcolumn, Prow, laberinto)
    if lista[-1] == 'S':
        if Grow + 1 < rows:
            if laberinto[Grow + 1][Gcolumn] == True or laberinto[Grow][Gcolumn-1] == "IP" or laberinto[Grow + 1][Gcolumn] == 'P' or laberinto[Grow + 1][Gcolumn] == 'Y':
                laberinto[Grow + 1][Gcolumn] = 'G'
                laberinto[Grow][Gcolumn] = True
                Grow += 1
                return laberinto
            else:
                return laberinto
        else:
            return laberinto
    elif lista[-1] == 'N':
        if Grow - 1 > 0:
            if laberinto[Grow - 1][Gcolumn] == True or laberinto[Grow][Gcolumn-1] == "IP" or laberinto[Grow - 1][Gcolumn] == 'P' or laberinto[Grow - 1][Gcolumn] == 'Y':
                laberinto[Grow - 1][Gcolumn] = 'G'
                laberinto[Grow][Gcolumn] = True
                Grow += 1
                return laberinto
            else:
                return laberinto
        else:
            return laberinto
    elif lista[-1] == 'O':
        if Gcolumn - 1 >= 0:
            if laberinto[Grow][Gcolumn-1] == True or laberinto[Grow][Gcolumn-1] == 'IP' or laberinto[Grow][Gcolumn-1] == 'P' or laberinto[Grow][Gcolumn-1] == 'Y':
                laberinto[Grow][Gcolumn-1] = 'G'
                laberinto[Grow][Gcolumn] = True
                Gcolumn -= 1
                return laberinto
            else:
                return laberinto
        else:
            return laberinto
    elif lista[-1] == 'E':
        if Gcolumn + 1 < cols:
            if laberinto[Grow][Gcolumn + 1] == True or laberinto[Grow][Gcolumn + 1] == 'IP' or laberinto[Grow][Gcolumn+1] == 'P' or laberinto[Grow][Gcolumn+1] == 'Y':
                laberinto[Grow][Gcolumn+1] = 'G'
                laberinto[Grow][Gcolumn] = True
                Gcolumn += 1
                return laberinto
            else:
                return laberinto
        else:
            return laberinto
    else:
        return laberinto

    
    











cols, rows = 50, 50
cell_size = 14
#Variables que describen las posibles direcciones en el laberinto.
N, S, E, W = 1, 2, 4, 8
directions = [N, S, E, W]
DX = {E:1, W:-1, N:0, S:0}
DY = {E:0, W:0, N:-1, S:1}
opposite = {E:W, W:E, N:S, S:N}

#Generamos el laberinto.

def generarLaberinto(x, y):
    laberinto[(x, y)] = True

    while True:
        sinVisitar = []
        if y > 1 and (x, y-2) not in visitado and y-2 > 0 and x> 0:
            sinVisitar.append('N')
        if y < rows-2 and (x, y+2) not in visitado and x > 0:
            sinVisitar.append('S')
        if x > 2 and (x-2, y) not in visitado and y > 0 and x-2 > 0:
            sinVisitar.append('O')
        if x < cols-2 and (x+2, y) not in visitado:
            sinVisitar.append('E')

        if len(sinVisitar) == 0 or visitado[-1][1]==rows-1 or visitado[-1][0]==cols-1:
            return
        else:
            siguiente = random.choice(sinVisitar)

            if siguiente == 'N':
                nextX = x
                nextY = y-2
                laberinto[(x, y-1)] = True
            elif siguiente == 'S':
                nextX = x
                nextY = y+2
                laberinto[(x, y+1)] = True
            elif siguiente == 'O':
                nextX = x-2
                nextY = y
                laberinto[(x-1, y)] = True
            elif siguiente == 'E':
                nextX = x+2
                nextY = y
                laberinto[(x+1, y)] = True

            visitado.append((nextX, nextY))
            generarLaberinto(nextX, nextY)





use_csv = False


   



if use_csv:
    #Lógica para archivos csv.
    pass
else:

    cols = 50
    rows = 50

    laberinto = {}
    for y in range(rows):
        for x in range(cols):
            laberinto[(x, y)] = False

    #Modo simple.
    visitado = [(1, 1)]
    generarLaberinto(0, 1)
    Matriz_ejemplo=[]
    for y in range(rows):
        row = []
        for x in range(cols):
            for key in laberinto.keys():
                if key[0]==x and key[1]==y:
                    row.append(laberinto[key])
        Matriz_ejemplo.append(row)
    Matriz_ejemplo[1][0]='P'
    for i in range(len(Matriz_ejemplo)):
        if Matriz_ejemplo[i][-1]==True:
            for j in range(i, len(Matriz_ejemplo)):
                Matriz_ejemplo[j][-1]=False
            for cell in Matriz_ejemplo[-1]:
                cell=False

    for i in range(len(Matriz_ejemplo[-1])):
        if Matriz_ejemplo[-1][i]==True:
            for j in range(i+1, len(Matriz_ejemplo[-1])):
                Matriz_ejemplo[-1][j]=False
        
    

    #Modo aventura.
    #Nivel 1
    visitado = [(1, 1)]
    generarLaberinto(0, 1)
    Matriz_aventura_1=[]
    for y in range(rows):
        row = []
        for x in range(cols):
            for key in laberinto.keys():
                if key[0]==x and key[1]==y:
                    row.append(laberinto[key])
        Matriz_aventura_1.append(row)

    for i in range(len(Matriz_aventura_1)):
        if Matriz_aventura_1[i][-1]==True:
            for j in range(i, len(Matriz_aventura_1)):
                Matriz_aventura_1[j][-1]=False
            for cell in Matriz_aventura_1[-1]:
                cell=False

    for i in range(len(Matriz_aventura_1[-1])):
        if Matriz_aventura_1[-1][i]==True:
            for j in range(i+1, len(Matriz_aventura_1[-1])):
                Matriz_aventura_1[-1][j]=False

    

    Py=random.randint(0, len(Matriz_aventura_1)-1)
    Px=random.randint(0, len(Matriz_aventura_1[0])-1)
    
    while Matriz_aventura_1[Py][Px]!=True:
        Py=random.randint(0, len(Matriz_aventura_1)-1)
        Px=random.randint(0, len(Matriz_aventura_1[0])-1)
    Matriz_aventura_1[Py][Px]='P'
    

    #Nivel 2
    visitado = [(1, 1)]
    generarLaberinto(0, 1)
    Matriz_aventura_2=[]
    for y in range(rows):
        row = []
        for x in range(cols):
            for key in laberinto.keys():
                if key[0]==x and key[1]==y:
                    row.append(laberinto[key])
        Matriz_aventura_2.append(row)

    for i in range(len(Matriz_aventura_2)):
        if Matriz_aventura_2[i][-1]==True:
            for j in range(i, len(Matriz_aventura_2)):
                Matriz_aventura_2[j][-1]=False
            for cell in Matriz_aventura_2[-1]:
                cell=False

    for i in range(len(Matriz_aventura_2[-1])):
        if Matriz_aventura_2[-1][i]==True:
            for j in range(i+1, len(Matriz_aventura_2[-1])):
                Matriz_aventura_2[-1][j]=False


        
    #Posición de inicio del jugador.
    Py=random.randint(0, len(Matriz_aventura_1)-1)
    Px=random.randint(0, len(Matriz_aventura_1[0])-1)
    while Matriz_aventura_2[Py][Px]!=True:
        Py=random.randint(0, len(Matriz_aventura_1)-1)
        Px=random.randint(0, len(Matriz_aventura_1[0])-1)
    Matriz_aventura_2[Py][Px]='P'

    By = random.randint(0, len(Matriz_aventura_2) - 1)
    Bx = random.randint(0, len(Matriz_aventura_2[0]) - 1)
    while Matriz_aventura_2[By][Bx] != True or (By == Py and Bx == Px):
        By = random.randint(0, len(Matriz_aventura_2) - 1)
        Bx = random.randint(0, len(Matriz_aventura_2[0]) - 1)
    Matriz_aventura_2[By][Bx] = 'B'

    

    #Nivel 3
    visitado = [(1, 1)]
    generarLaberinto(0, 1)
    Matriz_aventura_3=[]
    for y in range(rows):
        row = []
        for x in range(cols):
            for key in laberinto.keys():
                if key[0]==x and key[1]==y:
                    row.append(laberinto[key])
        Matriz_aventura_3.append(row)

    for i in range(len(Matriz_aventura_3)):
        if Matriz_aventura_3[i][-1]==True:
            for j in range(i, len(Matriz_aventura_3)):
                Matriz_aventura_3[j][-1]=False
            for cell in Matriz_aventura_3[-1]:
                cell=False

    for i in range(len(Matriz_aventura_3[-1])):
        if Matriz_aventura_3[-1][i]==True:
            for j in range(i+1, len(Matriz_aventura_3[-1])):
                Matriz_aventura_3[-1][j]=False

        

    #Posición de inicio del jugador.
    Py=random.randint(0, len(Matriz_aventura_1)-1)
    Px=random.randint(0, len(Matriz_aventura_1[0])-1)
    while Matriz_aventura_3[Py][Px]!=True:
        Py=random.randint(0, len(Matriz_aventura_1)-1)
        Px=random.randint(0, len(Matriz_aventura_1[0])-1)
    Matriz_aventura_3[Py][Px]='P'

    #Posición de inicio del monstruo.
    Py=random.randint(0, len(Matriz_aventura_1)-1)
    Px=random.randint(0, len(Matriz_aventura_1[0])-1)
    while Matriz_aventura_3[Py][Px]!=True:
        Py=random.randint(0, len(Matriz_aventura_1)-1)
        Px=random.randint(0, len(Matriz_aventura_1[0])-1)
    Matriz_aventura_3[Py][Px]='G'
    


    #Nivel 4
    visitado = [(1, 1)]
    generarLaberinto(0, 1)
    Matriz_aventura_4=[]
    for y in range(rows):
        row = []
        for x in range(cols):
            for key in laberinto.keys():
                if key[0]==x and key[1]==y:
                    row.append(laberinto[key])
        Matriz_aventura_4.append(row)

    for i in range(len(Matriz_aventura_4)):
        if Matriz_aventura_4[i][-1]==True:
            for j in range(i, len(Matriz_aventura_4)):
                Matriz_aventura_4[j][-1]=False
            for cell in Matriz_aventura_4[-1]:
                cell=False

    for i in range(len(Matriz_aventura_4[-1])):
        if Matriz_aventura_4[-1][i]==True:
            for j in range(i+1, len(Matriz_aventura_4[-1])):
                Matriz_aventura_4[-1][j]=False

    By = random.randint(0, len(Matriz_aventura_4) - 1)
    Bx = random.randint(0, len(Matriz_aventura_4[0]) - 1)
    while Matriz_aventura_4[By][Bx] != True or (By == Py and Bx == Px):
        By = random.randint(0, len(Matriz_aventura_4) - 1)
        Bx = random.randint(0, len(Matriz_aventura_4[0]) - 1)
    Matriz_aventura_4[By][Bx] = 'B'
        

    #Posición de inicio del jugador.
    Py=random.randint(0, len(Matriz_aventura_1)-1)
    Px=random.randint(0, len(Matriz_aventura_1[0])-1)
    while Matriz_aventura_4[Py][Px]!=True:
        Py=random.randint(0, len(Matriz_aventura_1)-1)
        Px=random.randint(0, len(Matriz_aventura_1[0])-1)
    Matriz_aventura_4[Py][Px]='P'

    #Posición de inicio del monstruo.
    Py=random.randint(0, len(Matriz_aventura_1)-1)
    Px=random.randint(0, len(Matriz_aventura_1[0])-1)
    while Matriz_aventura_4[Py][Px]!=True:
        Py=random.randint(0, len(Matriz_aventura_1)-1)
        Px=random.randint(0, len(Matriz_aventura_1[0])-1)
    Matriz_aventura_4[Py][Px]='G'
    

    #Modo competición.
    #Nivel 1
    visitado = [(1, 1)]
    generarLaberinto(0, 1)
    Matriz_competicion_1=[]
    for y in range(rows):
        row = []
        for x in range(cols):
            for key in laberinto.keys():
                if key[0]==x and key[1]==y:
                    row.append(laberinto[key])
        Matriz_competicion_1.append(row)

    for i in range(len(Matriz_competicion_1)):
        if Matriz_competicion_1[i][-1]==True:
            for j in range(i, len(Matriz_competicion_1)):
                Matriz_competicion_1[j][-1]=False
            for cell in Matriz_competicion_1[-1]:
                cell=False

    for i in range(len(Matriz_competicion_1[-1])):
        if Matriz_competicion_1[-1][i]==True:
            for j in range(i+1, len(Matriz_competicion_1[-1])):
                Matriz_competicion_1[-1][j]=False

        
        
    Py=random.randint(0, len(Matriz_competicion_1)-1)
    Px=random.randint(0, len(Matriz_competicion_1[0])-1)
    
    while Matriz_competicion_1[Py][Px]!=True:
        Py=random.randint(0, len(Matriz_competicion_1)-1)
        Px=random.randint(0, len(Matriz_competicion_1[0])-1)
    Matriz_competicion_1[Py][Px]='P'


    #Posición de inicio del jugador.
    Py=random.randint(0, len(Matriz_competicion_1)-1)
    Px=random.randint(0, len(Matriz_competicion_1[0])-1)
    while Matriz_competicion_1[Py][Px]!=True:
        Py=random.randint(0, len(Matriz_competicion_1)-1)
        Px=random.randint(0, len(Matriz_competicion_1[0])-1)
    Matriz_competicion_1[Py][Px]='Y'

    

    #Nivel 2
    visitado = [(1, 1)]
    generarLaberinto(0, 1)
    Matriz_competicion_2=[]
    for y in range(rows):
        row = []
        for x in range(cols):
            for key in laberinto.keys():
                if key[0]==x and key[1]==y:
                    row.append(laberinto[key])
        Matriz_competicion_2.append(row)

    for i in range(len(Matriz_competicion_2)):
        if Matriz_competicion_2[i][-1]==True:
            for j in range(i, len(Matriz_competicion_2)):
                Matriz_competicion_2[j][-1]=False
            for cell in Matriz_competicion_2[-1]:
                cell=False

    for i in range(len(Matriz_competicion_2[-1])):
        if Matriz_competicion_2[-1][i]==True:
            for j in range(i+1, len(Matriz_competicion_2[-1])):
                Matriz_competicion_2[-1][j]=False




    #Posición de inicio del jugador.     
    Py=random.randint(0, len(Matriz_competicion_1)-1)
    Px=random.randint(0, len(Matriz_competicion_1[0])-1)
    while Matriz_competicion_2[Py][Px]!=True:
        Py=random.randint(0, len(Matriz_competicion_1)-1)
        Px=random.randint(0, len(Matriz_competicion_1[0])-1)
    Matriz_competicion_2[Py][Px]='P'

    Py=random.randint(0, len(Matriz_competicion_1)-1)
    Px=random.randint(0, len(Matriz_competicion_1[0])-1)
    while Matriz_competicion_2[Py][Px]!=True:
        Py=random.randint(0, len(Matriz_competicion_1)-1)
        Px=random.randint(0, len(Matriz_competicion_1[0])-1)
    Matriz_competicion_2[Py][Px]='Y'



    #Nivel 3
    visitado = [(1, 1)]
    generarLaberinto(0, 1)
    Matriz_competicion_3=[]
    for y in range(rows):
        row = []
        for x in range(cols):
            for key in laberinto.keys():
                if key[0]==x and key[1]==y:
                    row.append(laberinto[key])
        Matriz_competicion_3.append(row)

    for i in range(len(Matriz_competicion_3)):
        if Matriz_competicion_3[i][-1]==True:
            for j in range(i, len(Matriz_competicion_3)):
                Matriz_competicion_3[j][-1]=False
            for cell in Matriz_competicion_3[-1]:
                cell=False

    for i in range(len(Matriz_competicion_3[-1])):
        if Matriz_competicion_3[-1][i]==True:
            for j in range(i+1, len(Matriz_competicion_3[-1])):
                Matriz_competicion_3[-1][j]=False



    #Posición de inicio del jugador.
    Py=random.randint(0, len(Matriz_competicion_1)-1)
    Px=random.randint(0, len(Matriz_competicion_1[0])-1)
    while Matriz_competicion_3[Py][Px]!=True:
        Py=random.randint(0, len(Matriz_competicion_1)-1)
        Px=random.randint(0, len(Matriz_competicion_1[0])-1)
    Matriz_competicion_3[Py][Px]='P'

    Py=random.randint(0, len(Matriz_competicion_1)-1)
    Px=random.randint(0, len(Matriz_competicion_1[0])-1)
    while Matriz_competicion_3[Py][Px]!=True:
        Py=random.randint(0, len(Matriz_competicion_1)-1)
        Px=random.randint(0, len(Matriz_competicion_1[0])-1)
    Matriz_competicion_3[Py][Px]='Y'

    #Posición de inicio del monstruo.
    Py=random.randint(0, len(Matriz_aventura_1)-1)
    Px=random.randint(0, len(Matriz_aventura_1[0])-1)
    while Matriz_competicion_3[Py][Px]!=True:
        Py=random.randint(0, len(Matriz_aventura_1)-1)
        Px=random.randint(0, len(Matriz_aventura_1[0])-1)
    Matriz_competicion_3[Py][Px]='G'


    #Nivel 4
    visitado = [(1, 1)]
    generarLaberinto(0, 1)
    Matriz_competicion_4=[]
    for y in range(rows):
        row = []
        for x in range(cols):
            for key in laberinto.keys():
                if key[0]==x and key[1]==y:
                    row.append(laberinto[key])
        Matriz_competicion_4.append(row)

    for i in range(len(Matriz_competicion_4)):
        if Matriz_competicion_4[i][-1]==True:
            for j in range(i, len(Matriz_competicion_4)):
                Matriz_competicion_4[j][-1]=False
            for cell in Matriz_competicion_4[-1]:
                cell=False

    for i in range(len(Matriz_competicion_4[-1])):
        if Matriz_competicion_4[-1][i]==True:
            for j in range(i+1, len(Matriz_competicion_4[-1])):
                Matriz_competicion_4[-1][j]=False
    

    #Posición de inicio del jugador.
    Py=random.randint(0, len(Matriz_competicion_1)-1)
    Px=random.randint(0, len(Matriz_competicion_1[0])-1)
    while Matriz_competicion_4[Py][Px]!=True:
        Py=random.randint(0, len(Matriz_competicion_1)-1)
        Px=random.randint(0, len(Matriz_competicion_1[0])-1)
    Matriz_competicion_4[Py][Px]='P'

    Py=random.randint(0, len(Matriz_competicion_1)-1)
    Px=random.randint(0, len(Matriz_competicion_1[0])-1)
    while Matriz_competicion_4[Py][Px]!=True:
        Py=random.randint(0, len(Matriz_competicion_1)-1)
        Px=random.randint(0, len(Matriz_competicion_1[0])-1)
    Matriz_competicion_4[Py][Px]='Y'

    #Posición de inicio del monstruo.
    Py=random.randint(0, len(Matriz_aventura_1)-1)
    Px=random.randint(0, len(Matriz_aventura_1[0])-1)
    while Matriz_competicion_4[Py][Px]!=True:
        Py=random.randint(0, len(Matriz_aventura_1)-1)
        Px=random.randint(0, len(Matriz_aventura_1[0])-1)
    Matriz_competicion_4[Py][Px]='G'

    
    
    

    #Auto
    if not use_csv:
        for i in range(len(Matriz_ejemplo)):
            if Matriz_ejemplo[i][-1]==True:
                Matriz_ejemplo[i][-1]='F'
        for i in range(len(Matriz_ejemplo[-1])):
            if Matriz_ejemplo[-1][i]==True:
                Matriz_ejemplo[-1][i]='F'
    lista_entradas=[]
    lista_salidas=[]
    for i in range(len(Matriz_ejemplo[0])):
        if Matriz_ejemplo[0][i]==True:
            lista_entradas.append((0,i))
    for i in range(len(Matriz_ejemplo[-1])):
        if Matriz_ejemplo[-1][i]==True:
            lista_entradas.append((-1,i))
    for i in range(len(Matriz_ejemplo)):
        if Matriz_ejemplo[i][0]==True:
            lista_entradas.append((i,0))
    for i in range(len(Matriz_ejemplo)):
        if Matriz_ejemplo[i][-1]==True:
            lista_entradas.append((i,-1))

    for i in range(len(Matriz_ejemplo[0])):
        if Matriz_ejemplo[0][i] == 'F':
            lista_salidas.append((0, i))
    # Borde inferior
    for i in range(len(Matriz_ejemplo[-1])):
        if Matriz_ejemplo[-1][i] == 'F':
            lista_salidas.append((len(Matriz_ejemplo) - 1, i))
    # Borde izquierdo
    for i in range(len(Matriz_ejemplo)):
        if Matriz_ejemplo[i][0] == 'F':
            lista_salidas.append((i, 0))
    # Borde derecho
    for i in range(len(Matriz_ejemplo)):
        if Matriz_ejemplo[i][-1] == 'F':
            lista_salidas.append((i, len(Matriz_ejemplo[0]) - 1))

        #Para la posicion de inicio
        def posiciones_borde_izquierda_arriba(matriz):
            filas = len(matriz)
            columnas = len(matriz[0])
            posiciones = []

            # Borde superior (fila 0)
            for j in range(columnas):
                if matriz[0][j] == True:
                    posiciones.append((0, j))

            # Borde izquierdo (columna 0), sin repetir la esquina (0,0)
            for i in range(1, filas):
                if matriz[i][0] == True:
                    posiciones.append((i, 0))

            return posiciones


        posibles_inicios = posiciones_borde_izquierda_arriba(Matriz_ejemplo)

        if posibles_inicios:
            Py, Px = random.choice(posibles_inicios)

        xm = None
        ym = None
        for i in range(len(Matriz_ejemplo)):
            for j in range(len(Matriz_ejemplo[i])):
                if Matriz_ejemplo[i][j] == 'F':
                    xm, ym =i, j
                    Matriz_ejemplo[i][j] = True
        if xm is None or ym is None:
            # Buscar en la última fila una celda True para ponerla como 'F'
            for j in range(len(Matriz_ejemplo[-1])):
                if Matriz_ejemplo[-1][j] == True:
                    xm, ym = len(Matriz_ejemplo) - 1, j
                    break
        if xm is None or ym is None:
            # Forzar solución: buscar en la última fila una celda que tenga encima un True
            for j in range(len(Matriz_ejemplo[-1])):
                if Matriz_ejemplo[-1][j] != True:  # Si no es True
                    # Verificamos que la celda encima sea True
                    if Matriz_ejemplo[-2][j] == True:
                        # Convertimos esta celda en 'F' y la asignamos como meta
                        Matriz_ejemplo[-1][j] = 'F'
                        xm, ym = len(Matriz_ejemplo) - 1, j
                        break
    Resuelto, pasos = Automatico(Matriz_ejemplo, 1, 0, xm, ym, [], 0)





    pygame.init()
    font = pygame.font.Font(None, 30)
    #ubicación del archivo que se usa en el fondo
    script_dir = os.path.dirname(os.path.realpath(__file__))
    if ambiente.lower()=='fire':
        fondo_path = os.path.join(script_dir, "..", "Images", 'Arenal_at_night.jpg')
    elif ambiente.lower()=='ice':
        fondo_path = os.path.join(script_dir, "..", "Images", 'K2.jpg')
    else:
    	fondo_path = os.path.join(script_dir, "..", "Images", 'supernova.jpg')

    fondo = pygame.image.load(fondo_path)


    width, height = cols * cell_size, rows * cell_size
    screen = pygame.display.set_mode((width, height),)
    pygame.display.set_caption('Juego')
    pygame.key.set_repeat(0)


    WHITE = (255, 255, 255)
    GRAY = (150, 150, 150)
    BLACK = (0, 0, 0)
    RED = (200, 0, 0)
    BLUE = (0, 0, 255)
    PURPLE = (128, 0, 128)
    YELLOW = (255, 165, 0)
    GREEN = (0, 255, 0)
    CELESTE = (0, 255, 255)
    SKY = (135, 206, 235)

    Ancho = 1920
    Alto = 1080
    matriz_Ancho = cols * cell_size
    matriz_Largo = rows * cell_size
    offset_x = (Ancho - matriz_Ancho) // 4
    offset_y = (Alto - matriz_Largo) // 15



    ventana = pygame.display.set_mode((Ancho,Alto),FULLSCREEN)
    clock = pygame.time.Clock()
    clock.tick(60)
    timestamp = time.time()
    while True:

        fondo = pygame.transform.scale(fondo, (Ancho, Alto))
        screen.blit(fondo, (0, 0))

        if modo.lower()=='simple':
            for y in range(len(Matriz_ejemplo)):
                row = Matriz_ejemplo[y]
                for x in range(len(row)):
                    cell = row[x]
                    rect = pygame.Rect(offset_x + x * cell_size, offset_y + y * cell_size, cell_size, cell_size)

                    if cell is True:
                        color = WHITE
                    elif cell is False:
                        color = GRAY
                    elif cell == "F":
                        color = RED
                    elif cell == "IP" or cell == "I":
                        color = BLUE
                    elif cell == 'P':
                        color = PURPLE
                        Prow,Pcolumn = y,x
                    else:
                        color = BLACK

                    # Estas líneas deben estar dentro del bucle interno
                    pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, BLACK, rect, 2)

            #Verificamos si el jugador ganó la partida.
            if 'P' in Matriz_ejemplo[-1]:
                pygame.quit()

            for row in Matriz_ejemplo:
                if row[-1]=='P':
                    pygame.quit()
            

            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        if Prow + 1 < rows:
                            if Matriz_ejemplo[Prow + 1][Pcolumn] == True or Matriz_ejemplo[Prow][Pcolumn-1] == "IP":
                                Matriz_ejemplo[Prow + 1][Pcolumn] = 'P'
                                Matriz_ejemplo[Prow][Pcolumn] = True
                                Prow += 1

                    elif event.key == pygame.K_UP:
                        if Prow-1 >= 0:
                            if Matriz_ejemplo[Prow - 1][Pcolumn] == True or Matriz_ejemplo[Prow][Pcolumn-1] == 'IP':
                                Matriz_ejemplo[Prow - 1][Pcolumn] = 'P'
                                Matriz_ejemplo[Prow][Pcolumn] = True
                                Prow -= 1

                    elif event.key == pygame.K_LEFT:
                        if Pcolumn - 1 >= 0:
                            if Matriz_ejemplo[Prow][Pcolumn-1] == True or Matriz_ejemplo[Prow][Pcolumn-1] == 'IP':
                                Matriz_ejemplo[Prow][Pcolumn-1] = 'P'
                                Matriz_ejemplo[Prow][Pcolumn] = True
                                Pcolumn -= 1
                    elif event.key == pygame.K_RIGHT:
                        if Pcolumn + 1 < cols:
                            if Matriz_ejemplo[Prow][Pcolumn + 1] == True or Matriz_ejemplo[Prow][Pcolumn + 1] == 'IP':
                                Matriz_ejemplo[Prow][Pcolumn+1] = 'P'
                                Matriz_ejemplo[Prow][Pcolumn] = True
                                Pcolumn += 1
        elif modo.lower() == 'automatic':

            if Resuelto:
                                    for y in range(len(Resuelto)):
                                        row = Resuelto[y]
                                        for x in range(len(row)):
                                            cell = row[x]
                                            rect = pygame.Rect(offset_x + x * cell_size, offset_y + y * cell_size,
                                                               cell_size, cell_size)

                                            if cell is True:
                                                color = WHITE
                                            elif cell is False:
                                                color = GRAY
                                            elif cell == "F":
                                                color = RED
                                            elif cell == "V" or cell == "I":
                                                color = BLUE
                                            elif cell == 'P':
                                                color = PURPLE
                                                Prow, Pcolumn = y, x
                                            else:
                                                color = BLACK
                                            pygame.draw.rect(screen, color, rect)

                                    # Mostrar cuadro de pasos
                                    cuadro_x = offset_x + len(Resuelto[0]) * cell_size + 20
                                    cuadro_y = offset_y
                                    cuadro_ancho = 120
                                    cuadro_alto = 60

                                    pygame.draw.rect(screen, (200, 200, 200),
                                                     (cuadro_x, cuadro_y, cuadro_ancho, cuadro_alto))
                                    pygame.draw.rect(screen, (0, 0, 0), (cuadro_x, cuadro_y, cuadro_ancho, cuadro_alto),
                                                     2)

                                    texto_titulo = font.render("Pasos:", True, (0, 0, 0))
                                    texto_num = font.render(str(pasos), True, (0, 0, 0))

                                    screen.blit(texto_titulo, (cuadro_x + 10, cuadro_y + 5))
                                    screen.blit(texto_num, (cuadro_x + 10, cuadro_y + 30))
                                    pygame.display.flip()

                                    # Bucle para mantener la ventana abierta hasta que el usuario la cierre
                                    esperando = True
                                    while esperando:
                                        for event in pygame.event.get():
                                            if event.type == pygame.QUIT:
                                                esperando = False
                                            if event.type == pygame.KEYDOWN:
                                                if event.key == pygame.K_ESCAPE:
                                                    esperando = False
                                    pygame.quit()

            else:
                                    # Mostrar mensaje de error si no hay solución
                                    cuadro_ancho = 300
                                    cuadro_alto = 150

                                    cuadro_x = (Ancho - cuadro_ancho) // 2
                                    cuadro_y = (Alto - cuadro_alto) // 2

                                    pygame.draw.rect(screen, (255, 200, 200),
                                                     (cuadro_x, cuadro_y, cuadro_ancho, cuadro_alto))
                                    pygame.draw.rect(screen, (255, 0, 0),
                                                     (cuadro_x, cuadro_y, cuadro_ancho, cuadro_alto), 4)

                                    texto = font.render("¡Laberinto sin solución!", True, (255, 0, 0))
                                    text_rect = texto.get_rect(
                                        center=(cuadro_x + cuadro_ancho // 2, cuadro_y + cuadro_alto // 2))
                                    screen.blit(texto, text_rect)
                                    pygame.display.flip()

                                    # Bucle para mantener la ventana abierta hasta que el usuario la cierre
                                    esperando = True
                                    while esperando:
                                        for event in pygame.event.get():
                                            if event.type == pygame.QUIT:
                                                esperando = False
                                            if event.type == pygame.KEYDOWN:
                                                if event.key == pygame.K_ESCAPE:
                                                    esperando = False
                                    pygame.quit()







        elif modo.lower()=='adventure':
            #Nivel 1
            if nivel1:
                
                
                for y in range(len(Matriz_aventura_1)):
                    row = Matriz_aventura_1[y]
                    for x in range(len(row)):
                        cell = row[x]
                        rect = pygame.Rect(offset_x + x * cell_size, offset_y + y * cell_size, cell_size, cell_size)

                        if cell is True:
                            color = WHITE
                        elif cell is False:
                            color = GRAY
                        elif cell == "F":
                            color = RED
                        elif cell == "B":
                            color = BLUE
                            PBrow,PBcolumn = y,x
                        elif cell == 'P':
                            color = PURPLE
                            Prow,Pcolumn = y,x
                        elif cell == 'Y':
                            color = YELLOW
                            Yrow, Ycolumn = y,x
                        elif cell == 'C':
                            color = CELESTE
                        else:
                            color = BLACK

                        # Estas líneas deben estar dentro del bucle interno
                        pygame.draw.rect(screen, color, rect)
                        pygame.draw.rect(screen, BLACK, rect, 2)

                #Verificamos si el jugador ganó la partida.
                if 'P' in Matriz_aventura_1[-1]:
                    timestamp = time.time()
                    nivel1=False

                for row in Matriz_aventura_1:
                    if row[-1]=='P' or row[-1]=='Y':
                        timestamp = time.time()
                        nivel1=False


                #Verificamos si han pasado 5 minutos.
                if time.time()-timestamp>=300:
                    pygame.quit()



                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    if event.type == pygame.KEYDOWN:
                        if jugador_congelado:
                            break
                        if event.key == pygame.K_DOWN:
                            if Prow + 1 < rows:
                                if Matriz_aventura_1[Prow + 1][Pcolumn] == True or Matriz_aventura_1[Prow][Pcolumn-1] == "IP":
                                    Matriz_aventura_1[Prow + 1][Pcolumn] = 'P'
                                    Matriz_aventura_1[Prow][Pcolumn] = True
                                    Prow += 1

                        elif event.key == pygame.K_UP:
                            if Prow-1 >= 0:
                                if Matriz_aventura_1[Prow - 1][Pcolumn] == True or Matriz_aventura_1[Prow][Pcolumn-1] == 'IP':
                                    Matriz_aventura_1[Prow - 1][Pcolumn] = 'P'
                                    Matriz_aventura_1[Prow][Pcolumn] = True
                                    Prow -= 1

                        elif event.key == pygame.K_LEFT:
                            if Pcolumn - 1 >= 0:
                                if Matriz_aventura_1[Prow][Pcolumn-1] == True or Matriz_aventura_1[Prow][Pcolumn-1] == 'IP':
                                    Matriz_aventura_1[Prow][Pcolumn-1] = 'P'
                                    Matriz_aventura_1[Prow][Pcolumn] = True
                                    Pcolumn -= 1
                        elif event.key == pygame.K_RIGHT:
                            if Pcolumn + 1 < cols:
                                if Matriz_aventura_1[Prow][Pcolumn + 1] == True or Matriz_aventura_1[Prow][Pcolumn + 1] == 'IP':
                                    Matriz_aventura_1[Prow][Pcolumn+1] = 'P'
                                    Matriz_aventura_1[Prow][Pcolumn] = True
                                    Pcolumn += 1


            #Nivel 2
            elif nivel2:
                Brow = None
                Bcolumn = None
                Prow = None
                Pcolumn = None

                # Pintar la matriz y detectar posiciones
                for y in range(len(Matriz_aventura_2)):
                    row = Matriz_aventura_2[y]
                    for x in range(len(row)):
                        cell = row[x]
                        rect = pygame.Rect(offset_x + x * cell_size, offset_y + y * cell_size, cell_size, cell_size)

                        if cell is True:
                            color = WHITE
                        elif cell is False:
                            color = GRAY
                        elif cell == "F":
                            color = RED
                        elif cell == "B":
                            color = BLUE
                            Brow, Bcolumn = y, x
                        elif cell == 'P':
                            color = PURPLE
                            Prow, Pcolumn = y, x
                        elif cell == 'Y':
                            color = YELLOW
                            Yrow, Ycolumn = y, x
                        elif cell == 'C':
                            color = CELESTE
                        else:
                            color = BLACK

                        pygame.draw.rect(screen, color, rect)
                        pygame.draw.rect(screen, BLACK, rect, 2)

                # Comprobar si el jugador llegó al final para terminar nivel
                if 'P' in Matriz_aventura_2[-1]:
                    timestamp = time.time()
                    nivel2 = False

                for row in Matriz_aventura_2:
                    if row[-1] == 'P':
                        timestamp = time.time()
                        nivel2 = False

                # Verificar si ya pasó el tiempo límite del juego
                if time.time() - timestamp >= 300:
                    print('Game Over')
                    pygame.quit()
                    exit()

                rows = len(Matriz_aventura_2)
                cols = len(Matriz_aventura_2[0])
                tiempo_actual = time.time()

                # Control de congelamiento
                if Prow is not None and Brow is not None:
                    tocando = esta_tocando(Prow, Pcolumn, Brow, Bcolumn)
                else:
                    tocando = False

                if tocando:
                    if not jugador_congelado:
                        jugador_congelado = True
                        tiempo_congelado_inicio = tiempo_actual
                        Matriz_aventura_2[Prow][Pcolumn] = 'C'
                else:
                    if jugador_congelado and tiempo_congelado_inicio is not None:
                        if tiempo_actual - tiempo_congelado_inicio >= duracion_congelado:
                            jugador_congelado = False
                            tiempo_congelado_inicio = None
                            for y in range(rows):
                                for x in range(cols):
                                    if Matriz_aventura_2[y][x] == 'C':
                                        Matriz_aventura_2[y][x] = 'P'

                pygame.display.flip()

                # Movimiento del jugador solo si no está congelado
                if not jugador_congelado and Prow is not None and Pcolumn is not None:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            exit()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_DOWN:
                                if Prow + 1 < rows:
                                    if Matriz_aventura_2[Prow + 1][Pcolumn] == True or Matriz_aventura_2[Prow][
                                        Pcolumn - 1] == "IP":
                                        Matriz_aventura_2[Prow + 1][Pcolumn] = 'P'
                                        Matriz_aventura_2[Prow][Pcolumn] = True
                                        Prow += 1

                            elif event.key == pygame.K_UP:
                                if Prow - 1 >= 0:
                                    if Matriz_aventura_2[Prow - 1][Pcolumn] == True or Matriz_aventura_2[Prow][
                                        Pcolumn - 1] == 'IP':
                                        Matriz_aventura_2[Prow - 1][Pcolumn] = 'P'
                                        Matriz_aventura_2[Prow][Pcolumn] = True
                                        Prow -= 1

                            elif event.key == pygame.K_LEFT:
                                if Pcolumn - 1 >= 0:
                                    if Matriz_aventura_2[Prow][Pcolumn - 1] == True or Matriz_aventura_2[Prow][
                                        Pcolumn - 1] == 'IP':
                                        Matriz_aventura_2[Prow][Pcolumn - 1] = 'P'
                                        Matriz_aventura_2[Prow][Pcolumn] = True
                                        Pcolumn -= 1

                            elif event.key == pygame.K_RIGHT:
                                if Pcolumn + 1 < cols:
                                    if Matriz_aventura_2[Prow][Pcolumn + 1] == True or Matriz_aventura_2[Prow][
                                        Pcolumn + 1] == 'IP':
                                        Matriz_aventura_2[Prow][Pcolumn + 1] = 'P'
                                        Matriz_aventura_2[Prow][Pcolumn] = True
                                        Pcolumn += 1

                # Movimiento del bicho azul según tu función moverAzulAventura
                if time.time() - tiempo_ultimo_movimiento_bicho >= delay_movimiento_bicho:
                    Matriz_aventura_2, tiempo_congelado_inicio, jugador_congelado = moverAzulAventura(
                        Bcolumn, Brow, Matriz_aventura_2, jugador_congelado)
                    tiempo_ultimo_movimiento_bicho = time.time()


            #Nivel 3
            elif nivel3:


                
                for y in range(len(Matriz_aventura_3)):
                    row = Matriz_aventura_3[y]
                    for x in range(len(row)):
                        cell = row[x]
                        rect = pygame.Rect(offset_x + x * cell_size, offset_y + y * cell_size, cell_size, cell_size)

                        if cell is True:
                            color = WHITE
                        elif cell is False:
                            color = GRAY
                        elif cell == "F":
                            color = RED
                        elif cell == "B":
                            color = BLUE
                            Brow, Bcolumn = y, x
                            PBrow,PBcolumn = y,x
                        elif cell == 'P':
                            color = PURPLE
                            Prow,Pcolumn = y,x
                        elif cell == 'Y':
                            color = YELLOW
                            Yrow, Ycolumn = y,x
                        elif cell == 'G':
                            color = GREEN
                            Grow, Gcolumn = y,x
                        else:
                            color = BLACK

                        # Estas líneas deben estar dentro del bucle interno
                        pygame.draw.rect(screen, color, rect)
                        pygame.draw.rect(screen, BLACK, rect, 2)

                #Verificamos si el jugador ganó la partida.
                if 'P' in Matriz_aventura_3[-1]:
                    timestamp = time.time()
                    nivel3=False

                for row in Matriz_aventura_3:
                    if row[-1]=='P':
                        timestamp = time.time()
                        nivel3=False


                #Verificamos si han pasado 5 minutos.
                if time.time()-timestamp>=300:
                    pygame.quit()
                    


                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_DOWN:
                            if Prow + 1 < rows:
                                if Matriz_aventura_3[Prow + 1][Pcolumn] == True or Matriz_aventura_3[Prow][Pcolumn-1] == "IP":
                                    Matriz_aventura_3[Prow + 1][Pcolumn] = 'P'
                                    Matriz_aventura_3[Prow][Pcolumn] = True
                                    Prow += 1
                            
                            

                        elif event.key == pygame.K_UP:
                            if Prow-1 >= 0:
                                if Matriz_aventura_3[Prow - 1][Pcolumn] == True or Matriz_aventura_3[Prow][Pcolumn-1] == 'IP':
                                    Matriz_aventura_3[Prow - 1][Pcolumn] = 'P'
                                    Matriz_aventura_3[Prow][Pcolumn] = True
                                    Prow -= 1

                        elif event.key == pygame.K_LEFT:
                            if Pcolumn - 1 >= 0:
                                if Matriz_aventura_3[Prow][Pcolumn-1] == True or Matriz_aventura_3[Prow][Pcolumn-1] == 'IP':
                                    Matriz_aventura_3[Prow][Pcolumn-1] = 'P'
                                    Matriz_aventura_3[Prow][Pcolumn] = True
                                    Pcolumn -= 1
                        elif event.key == pygame.K_RIGHT:
                            if Pcolumn + 1 < cols:
                                if Matriz_aventura_3[Prow][Pcolumn + 1] == True or Matriz_aventura_3[Prow][Pcolumn + 1] == 'IP':
                                    Matriz_aventura_3[Prow][Pcolumn+1] = 'P'
                                    Matriz_aventura_3[Prow][Pcolumn] = True
                                    Pcolumn += 1

                        Matriz_aventura_3 = moverVerdeAventura(Gcolumn, Grow, Pcolumn, Prow, Matriz_aventura_3)

                        



            #Nivel 4
            elif nivel4:

                for y in range(len(Matriz_aventura_4)):
                    row = Matriz_aventura_4[y]
                    for x in range(len(row)):
                        cell = row[x]
                        rect = pygame.Rect(offset_x + x * cell_size, offset_y + y * cell_size, cell_size, cell_size)

                        if cell is True:
                            color = WHITE
                        elif cell is False:
                            color = GRAY
                        elif cell == "F":
                            color = RED
                        elif cell == "B":
                            color = BLUE
                            PBrow, PBcolumn = y, x
                        elif cell == 'P':
                            color = PURPLE
                            Prow, Pcolumn = y, x
                        elif cell == 'Y':
                            color = YELLOW
                            Yrow, Ycolumn = y, x
                        elif cell == 'G':
                            color = GREEN
                            Grow, Gcolumn = y, x
                        elif cell == 'C':
                            color = CELESTE
                        else:
                            color = BLACK

                        pygame.draw.rect(screen, color, rect)
                        pygame.draw.rect(screen, BLACK, rect, 2)

                # Verificamos si el jugador ganó la partida.
                if 'P' in Matriz_aventura_4[-1]:
                    print('¡Ganaste!')
                    pygame.quit()
                    exit()

                for row in Matriz_aventura_4:
                    if row[-1] == 'P':
                        print('¡Ganaste!')
                        pygame.quit()
                        exit()

                # Verificamos si han pasado 5 minutos.
                if time.time() - timestamp >= 300:
                    print('¡Perdiste!')
                    pygame.quit()
                    exit()

                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_DOWN:
                            if Prow + 1 < rows:
                                if Matriz_aventura_4[Prow + 1][Pcolumn] == True or Matriz_aventura_4[Prow][
                                    Pcolumn - 1] == "IP":
                                    Matriz_aventura_4[Prow + 1][Pcolumn] = 'P'
                                    Matriz_aventura_4[Prow][Pcolumn] = True
                                    Prow += 1

                        elif event.key == pygame.K_UP:
                            if Prow - 1 >= 0:
                                if Matriz_aventura_4[Prow - 1][Pcolumn] == True or Matriz_aventura_4[Prow][
                                    Pcolumn - 1] == 'IP':
                                    Matriz_aventura_4[Prow - 1][Pcolumn] = 'P'
                                    Matriz_aventura_4[Prow][Pcolumn] = True
                                    Prow -= 1

                        elif event.key == pygame.K_LEFT:
                            if Pcolumn - 1 >= 0:
                                if Matriz_aventura_4[Prow][Pcolumn - 1] == True or Matriz_aventura_4[Prow][
                                    Pcolumn - 1] == 'IP':
                                    Matriz_aventura_4[Prow][Pcolumn - 1] = 'P'
                                    Matriz_aventura_4[Prow][Pcolumn] = True
                                    Pcolumn -= 1
                        elif event.key == pygame.K_RIGHT:
                            if Pcolumn + 1 < cols:
                                if Matriz_aventura_4[Prow][Pcolumn + 1] == True or Matriz_aventura_4[Prow][
                                    Pcolumn + 1] == 'IP':
                                    Matriz_aventura_4[Prow][Pcolumn + 1] = 'P'
                                    Matriz_aventura_4[Prow][Pcolumn] = True
                                    Pcolumn += 1

                        Matriz_aventura_4 = moverVerdeAventura(Gcolumn, Grow, Pcolumn, Prow, Matriz_aventura_4)

                # Movemos el bicho azul con retardo, igual que en nivel 2
                if time.time() - tiempo_ultimo_movimiento_bicho >= delay_movimiento_bicho:
                    Matriz_aventura_4, _, _ = moverAzulAventura(PBcolumn, PBrow, Matriz_aventura_4,
                                                                jugador_congelado=False)
                    tiempo_ultimo_movimiento_bicho = time.time()




        elif modo.lower()=='competition':
        
        	conn = sqlite3.connect('scores.db')
        	c = conn.cursor()
        	c.execute('''CREATE TABLE IF NOT EXISTS scores (
        					id INTEGER PRIMARY KEY,
        					player TEXT NOT NULL,
        					score INTEGER NOT NULL
        					);''')
        	players = [
        				('Purple', 0),
        				('Orange', 0)
        				]
        	c.executemany('INSERT INTO scores (player, score) VALUES (?, ?)', players)
        	
        	
        
            #Nivel 1
            if nivel1:


                
                for y in range(len(Matriz_competicion_1)):
                    row = Matriz_competicion_1[y]
                    for x in range(len(row)):
                        cell = row[x]
                        rect = pygame.Rect(offset_x + x * cell_size, offset_y + y * cell_size, cell_size, cell_size)

                        if cell is True:
                            color = WHITE
                        elif cell is False:
                            color = GRAY
                        elif cell == "F":
                            color = RED
                        elif cell == "B":
                            color = BLUE
                            PBrow,PBcolumn = y,x
                        elif cell == 'P':
                            color = PURPLE
                            Prow,Pcolumn = y,x
                        elif cell == 'Y':
                            color = YELLOW
                            Yrow, Ycolumn = y,x
                        else:
                            color = BLACK

                        # Estas líneas deben estar dentro del bucle interno
                        pygame.draw.rect(screen, color, rect)
                        pygame.draw.rect(screen, BLACK, rect, 2)

                #Verificamos si el jugador ganó la partida.
                if 'P' in Matriz_competicion_1[-1]:
                    #puntosP+=1
                    c.execute('''UPDATE scores
                    				SET score = score + 1
                    				WHERE player = "Purple";'''
                    				)
                    
                    timestamp = time.time()
                    nivel1=False
                elif 'Y' in Matriz_competicion_1[-1]:
                    #puntosY+=1
                    c.execute('''UPDATE scores
                    				SET score = score + 1
                    				WHERE player = "Orange";'''
                    				)
                    
                    timestamp = time.time()
                    nivel1=False

                for row in Matriz_competicion_1:
                    if row[-1]=='P':
                        puntosP+=1
                        timestamp = time.time()
                        nivel1=False
                    elif row[-1]=='Y':
                        puntosY+=1
                        timestamp = time.time()
                        nivel1=False
                        


                #Verificamos si han pasado 5 minutos.
                if time.time()-timestamp>=300:
                    pygame.quit()
                    


                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_DOWN:
                            if Prow + 1 < rows:
                                if Matriz_competicion_1[Prow + 1][Pcolumn] == True or Matriz_competicion_1[Prow][Pcolumn-1] == "IP":
                                    Matriz_competicion_1[Prow + 1][Pcolumn] = 'P'
                                    Matriz_competicion_1[Prow][Pcolumn] = True
                                    Prow += 1

                        elif event.key == pygame.K_UP:
                            if Prow-1 >= 0:
                                if Matriz_competicion_1[Prow - 1][Pcolumn] == True or Matriz_competicion_1[Prow][Pcolumn-1] == 'IP':
                                    Matriz_competicion_1[Prow - 1][Pcolumn] = 'P'
                                    Matriz_competicion_1[Prow][Pcolumn] = True
                                    Prow -= 1

                        elif event.key == pygame.K_LEFT:
                            if Pcolumn - 1 >= 0:
                                if Matriz_competicion_1[Prow][Pcolumn-1] == True or Matriz_competicion_1[Prow][Pcolumn-1] == 'IP':
                                    Matriz_competicion_1[Prow][Pcolumn-1] = 'P'
                                    Matriz_competicion_1[Prow][Pcolumn] = True
                                    Pcolumn -= 1
                        elif event.key == pygame.K_RIGHT:
                            if Pcolumn + 1 < cols:
                                if Matriz_competicion_1[Prow][Pcolumn + 1] == True or Matriz_competicion_1[Prow][Pcolumn + 1] == 'IP':
                                    Matriz_competicion_1[Prow][Pcolumn+1] = 'P'
                                    Matriz_competicion_1[Prow][Pcolumn] = True
                                    Pcolumn += 1

                        elif event.key == pygame.K_s:
                            if Yrow + 1 < rows:
                                if Matriz_competicion_1[Yrow + 1][Ycolumn] == True or Matriz_competicion_1[Yrow][Ycolumn-1] == "IP":
                                    Matriz_competicion_1[Yrow + 1][Ycolumn] = 'Y'
                                    Matriz_competicion_1[Yrow][Ycolumn] = True
                                    Yrow += 1

                        elif event.key == pygame.K_w:
                            if Yrow-1 >= 0:
                                if Matriz_competicion_1[Yrow - 1][Ycolumn] == True or Matriz_competicion_1[Yrow][Ycolumn-1] == 'IP':
                                    Matriz_competicion_1[Yrow - 1][Ycolumn] = 'Y'
                                    Matriz_competicion_1[Yrow][Ycolumn] = True
                                    Yrow -= 1

                        elif event.key == pygame.K_a:
                            if Ycolumn - 1 >= 0:
                                if Matriz_competicion_1[Yrow][Ycolumn-1] == True or Matriz_competicion_1[Yrow][Ycolumn-1] == 'IP':
                                    Matriz_competicion_1[Yrow][Ycolumn-1] = 'Y'
                                    Matriz_competicion_1[Yrow][Ycolumn] = True
                                    Ycolumn -= 1
                        elif event.key == pygame.K_d:
                            if Ycolumn + 1 < cols:
                                if Matriz_competicion_1[Yrow][Ycolumn + 1] == True or Matriz_competicion_1[Yrow][Ycolumn + 1] == 'IP':
                                    Matriz_competicion_1[Yrow][Ycolumn+1] = 'Y'
                                    Matriz_competicion_1[Yrow][Ycolumn] = True
                                    Ycolumn += 1

                        


            #Nivel 2
            elif nivel2:



                
                for y in range(len(Matriz_competicion_2)):
                    row = Matriz_competicion_2[y]
                    for x in range(len(row)):
                        cell = row[x]
                        rect = pygame.Rect(offset_x + x * cell_size, offset_y + y * cell_size, cell_size, cell_size)

                        if cell is True:
                            color = WHITE
                        elif cell is False:
                            color = GRAY
                        elif cell == "F":
                            color = RED
                        elif cell == "B":
                            color = BLUE
                            PBrow,PBcolumn = y,x
                        elif cell == 'P':
                            color = PURPLE
                            Prow,Pcolumn = y,x
                        elif cell == 'Y':
                            color = YELLOW
                            Yrow, Ycolumn = y,x
                        else:
                            color = BLACK

                        # Estas líneas deben estar dentro del bucle interno
                        pygame.draw.rect(screen, color, rect)
                        pygame.draw.rect(screen, BLACK, rect, 2)

                #Verificamos si el jugador ganó la partida.
                if 'P' in Matriz_competicion_2[-1]:
                    #puntosP+=1
                    c.execute('''UPDATE scores
                    				SET score = score + 1
                    				WHERE player = "Purple";'''
                    				)
                    timestamp = time.time()
                    nivel2=False
                elif 'Y' in Matriz_competicion_2[-1]:
                    #puntosY+=1
                    c.execute('''UPDATE scores
                    				SET score = score + 1
                    				WHERE player = "Orange";'''
                    				)
                    timestamp = time.time()
                    nivel2=False

                for row in Matriz_competicion_2:
                    if row[-1]=='P':
                        puntosP+=1
                        timestamp = time.time()
                        nivel2=False
                    elif row[-1]=='Y':
                        puntosY+=1
                        timestamp = time.time()
                        nivel2=False


                #Verificamos si han pasado 5 minutos.
                if time.time()-timestamp>=300:
                    pygame.quit()
                    


                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_DOWN:
                            if Prow + 1 < rows:
                                if Matriz_competicion_2[Prow + 1][Pcolumn] == True or Matriz_competicion_2[Prow][Pcolumn-1] == "IP":
                                    Matriz_competicion_2[Prow + 1][Pcolumn] = 'P'
                                    Matriz_competicion_2[Prow][Pcolumn] = True
                                    Prow += 1

                        elif event.key == pygame.K_UP:
                            if Prow-1 >= 0:
                                if Matriz_competicion_2[Prow - 1][Pcolumn] == True or Matriz_competicion_2[Prow][Pcolumn-1] == 'IP':
                                    Matriz_competicion_2[Prow - 1][Pcolumn] = 'P'
                                    Matriz_competicion_2[Prow][Pcolumn] = True
                                    Prow -= 1

                        elif event.key == pygame.K_LEFT:
                            if Pcolumn - 1 >= 0:
                                if Matriz_competicion_2[Prow][Pcolumn-1] == True or Matriz_competicion_2[Prow][Pcolumn-1] == 'IP':
                                    Matriz_competicion_2[Prow][Pcolumn-1] = 'P'
                                    Matriz_competicion_2[Prow][Pcolumn] = True
                                    Pcolumn -= 1
                        elif event.key == pygame.K_RIGHT:
                            if Pcolumn + 1 < cols:
                                if Matriz_competicion_2[Prow][Pcolumn + 1] == True or Matriz_competicion_2[Prow][Pcolumn + 1] == 'IP':
                                    Matriz_competicion_2[Prow][Pcolumn+1] = 'P'
                                    Matriz_competicion_2[Prow][Pcolumn] = True
                                    Pcolumn += 1


                        elif event.key == pygame.K_s:
                            if Yrow + 1 < rows:
                                if Matriz_competicion_2[Yrow + 1][Ycolumn] == True or Matriz_competicion_2[Yrow][Ycolumn-1] == "IP":
                                    Matriz_competicion_2[Yrow + 1][Ycolumn] = 'Y'
                                    Matriz_competicion_2[Yrow][Ycolumn] = True
                                    Yrow += 1

                        elif event.key == pygame.K_w:
                            if Yrow-1 >= 0:
                                if Matriz_competicion_2[Yrow - 1][Ycolumn] == True or Matriz_competicion_2[Yrow][Ycolumn-1] == 'IP':
                                    Matriz_competicion_2[Yrow - 1][Ycolumn] = 'Y'
                                    Matriz_competicion_2[Yrow][Ycolumn] = True
                                    Yrow -= 1

                        elif event.key == pygame.K_a:
                            if Ycolumn - 1 >= 0:
                                if Matriz_competicion_2[Yrow][Ycolumn-1] == True or Matriz_competicion_2[Yrow][Ycolumn-1] == 'IP':
                                    Matriz_competicion_2[Yrow][Ycolumn-1] = 'Y'
                                    Matriz_competicion_2[Yrow][Ycolumn] = True
                                    Ycolumn -= 1
                        elif event.key == pygame.K_d:
                            if Ycolumn + 1 < cols:
                                if Matriz_competicion_2[Yrow][Ycolumn + 1] == True or Matriz_competicion_2[Yrow][Ycolumn + 1] == 'IP':
                                    Matriz_competicion_2[Yrow][Ycolumn+1] = 'Y'
                                    Matriz_competicion_2[Yrow][Ycolumn] = True
                                    Ycolumn += 1



            #Nivel 3
            elif nivel3:
                if not any('P' in row or 'Y' in row for row in Matriz_competicion_3):
                    print("¡Perdieron!")
                    pygame.quit()
                    exit()

                for y in range(len(Matriz_competicion_3)):
                    row = Matriz_competicion_3[y]
                    for x in range(len(row)):
                        cell = row[x]
                        rect = pygame.Rect(offset_x + x * cell_size, offset_y + y * cell_size, cell_size, cell_size)

                        if cell is True:
                            color = WHITE
                        elif cell is False:
                            color = GRAY
                        elif cell == "F":
                            color = RED
                        elif cell == "B":
                            color = BLUE
                            PBrow,PBcolumn = y,x
                        elif cell == 'P':
                            color = PURPLE
                            Prow,Pcolumn = y,x
                        elif cell == 'Y':
                            color = YELLOW
                            Yrow, Ycolumn = y,x
                        elif cell == 'G':
                            color = GREEN
                            Grow, Gcolumn = y,x
                        else:
                            color = BLACK

                        # Estas líneas deben estar dentro del bucle interno
                        pygame.draw.rect(screen, color, rect)
                        pygame.draw.rect(screen, BLACK, rect, 2)

                #Verificamos si el jugador ganó la partida.
                if 'P' in Matriz_competicion_3[-1]:
                    #puntosP+=1
                    c.execute('''UPDATE scores
                    				SET score = score + 1
                    				WHERE player = "Purple";'''
                    				)
                    				
                    timestamp = time.time()
                    nivel3=False
                elif 'Y' in Matriz_competicion_3[-1]:
                    #puntosY+=1
                    c.execute('''UPDATE scores
                    				SET score = score + 1
                    				WHERE player = "Orange";'''
                    				)
                    timestamp = time.time()
                    nivel3=False

                for row in Matriz_competicion_3:
                    if row[-1]=='P':
                        puntosP+=1
                        timestamp = time.time()
                        nivel3=False
                    elif row[-1]=='Y':
                        puntosY+=1
                        timestamp = time.time()
                        nivel3=False



                #Verificamos si han pasado 5 minutos.
                if time.time()-timestamp>=300:
                    pygame.quit()
                    


                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_DOWN and Matriz_competicion_3[Prow][Pcolumn] == 'P':
                            if Prow + 1 < rows:
                                if Matriz_competicion_3[Prow + 1][Pcolumn] == True or Matriz_competicion_3[Prow][Pcolumn-1] == "IP":
                                    Matriz_competicion_3[Prow + 1][Pcolumn] = 'P'
                                    Matriz_competicion_3[Prow][Pcolumn] = True
                                    Prow += 1

                        elif event.key == pygame.K_UP and Matriz_competicion_3[Prow][Pcolumn] == 'P':
                            if Prow-1 >= 0:
                                if Matriz_competicion_3[Prow - 1][Pcolumn] == True or Matriz_competicion_3[Prow][Pcolumn-1] == 'IP':
                                    Matriz_competicion_3[Prow - 1][Pcolumn] = 'P'
                                    Matriz_competicion_3[Prow][Pcolumn] = True
                                    Prow -= 1

                        elif event.key == pygame.K_LEFT and Matriz_competicion_3[Prow][Pcolumn] == 'P':
                            if Pcolumn - 1 >= 0:
                                if Matriz_competicion_3[Prow][Pcolumn-1] == True or Matriz_competicion_3[Prow][Pcolumn-1] == 'IP':
                                    Matriz_competicion_3[Prow][Pcolumn-1] = 'P'
                                    Matriz_competicion_3[Prow][Pcolumn] = True
                                    Pcolumn -= 1
                        elif event.key == pygame.K_RIGHT and Matriz_competicion_3[Prow][Pcolumn] == 'P':
                            if Pcolumn + 1 < cols:
                                if Matriz_competicion_3[Prow][Pcolumn + 1] == True or Matriz_competicion_3[Prow][Pcolumn + 1] == 'IP':
                                    Matriz_competicion_3[Prow][Pcolumn+1] = 'P'
                                    Matriz_competicion_3[Prow][Pcolumn] = True
                                    Pcolumn += 1


                        elif event.key == pygame.K_s and Matriz_competicion_3[Yrow][Ycolumn] == 'Y':
                            if Yrow + 1 < rows:
                                if Matriz_competicion_3[Yrow + 1][Ycolumn] == True or Matriz_competicion_3[Yrow][Ycolumn-1] == "IP":
                                    Matriz_competicion_3[Yrow + 1][Ycolumn] = 'Y'
                                    Matriz_competicion_3[Yrow][Ycolumn] = True
                                    Yrow += 1

                        elif event.key == pygame.K_w and Matriz_competicion_3[Yrow][Ycolumn] == 'Y':
                            if Yrow-1 >= 0:
                                if Matriz_competicion_3[Yrow - 1][Ycolumn] == True or Matriz_competicion_3[Yrow][Ycolumn-1] == 'IP':
                                    Matriz_competicion_3[Yrow - 1][Ycolumn] = 'Y'
                                    Matriz_competicion_3[Yrow][Ycolumn] = True
                                    Yrow -= 1

                        elif event.key == pygame.K_a and Matriz_competicion_3[Yrow][Ycolumn] == 'Y':
                            if Ycolumn - 1 >= 0:
                                if Matriz_competicion_3[Yrow][Ycolumn-1] == True or Matriz_competicion_3[Yrow][Ycolumn-1] == 'IP':
                                    Matriz_competicion_3[Yrow][Ycolumn-1] = 'Y'
                                    Matriz_competicion_3[Yrow][Ycolumn] = True
                                    Ycolumn -= 1
                        elif event.key == pygame.K_d and Matriz_competicion_3[Yrow][Ycolumn] == 'Y':
                            if Ycolumn + 1 < cols:
                                if Matriz_competicion_3[Yrow][Ycolumn + 1] == True or Matriz_competicion_3[Yrow][Ycolumn + 1] == 'IP':
                                    Matriz_competicion_3[Yrow][Ycolumn+1] = 'Y'
                                    Matriz_competicion_3[Yrow][Ycolumn] = True
                                    Ycolumn += 1

                        if Matriz_competicion_3[Prow][Pcolumn] == 'P':
                            Matriz_competicion_3 = moverVerdeCompeticion(Gcolumn, Grow, Pcolumn, Prow, Matriz_competicion_3)
                        else:
                            Matriz_competicion_3 = moverVerdeCompeticion(Gcolumn, Grow, Ycolumn, Yrow,Matriz_competicion_3)



            #Nivel 4
            elif nivel4:
                if not any('P' in row or 'Y' in row for row in Matriz_competicion_4):
                    print("¡Perdieron!")
                    pygame.quit()
                    exit()

                for y in range(len(Matriz_competicion_4)):
                    row = Matriz_competicion_4[y]
                    for x in range(len(row)):
                        cell = row[x]
                        rect = pygame.Rect(offset_x + x * cell_size, offset_y + y * cell_size, cell_size, cell_size)

                        if cell is True:
                            color = WHITE
                        elif cell is False:
                            color = GRAY
                        elif cell == "F":
                            color = RED
                        elif cell == "B":
                            color = BLUE
                            PBrow,PBcolumn = y,x
                        elif cell == 'P':
                            color = PURPLE
                            Prow,Pcolumn = y,x
                        elif cell == 'Y':
                            color = YELLOW
                            Yrow, Ycolumn = y,x
                        elif cell == 'G':
                            color = GREEN
                            Grow, Gcolumn = y,x
                        else:
                            color = BLACK

                        # Estas líneas deben estar dentro del bucle interno
                        pygame.draw.rect(screen, color, rect)
                        pygame.draw.rect(screen, BLACK, rect, 2)

                #Verificamos si el jugador ganó la partida.
                if 'P' in Matriz_competicion_4[-1]:
                	puntosP = c.execute('SELECT score FROM scores WHERE player = "Purple"')
                	PuntosY = c.execute('SELECT score FROM scores WHERE player = "Orange"')
                    #puntosP+=1
                    c.execute('''UPDATE scores
                    				SET score = score + 1
                    				WHERE player = "Purple";'''
                    				)
                    try:
                        pygame.quit()
                    except:
                        if puntosP>puntosY:
                            print('Purple wins!')
                        elif puntosP<puntosY:
                            print('Orange wins!')
                        else:
                            print('Draw!')
                elif 'Y' in Matriz_competicion_4[-1]:
                	puntosP = c.execute('SELECT score FROM scores WHERE player = "Purple"')
                	PuntosY = c.execute('SELECT score FROM scores WHERE player = "Orange"')
                    #puntosY+=1
                    c.execute('''UPDATE scores
                    				SET score = score + 1
                    				WHERE player = "Orange";'''
                    				)
                    try:
                        pygame.quit()
                    except:
                        if puntosP>puntosY:
                            print('Purple wins!')
                        elif puntosP<puntosY:
                            print('Orange wins!')
                        else:
                            print('Draw!')
                for row in Matriz_competicion_4:
                    if row[-1]=='P':
                        puntosP = c.execute('SELECT score FROM scores WHERE player = "Purple"')
                		PuntosY = c.execute('SELECT score FROM scores WHERE player = "Orange"')
                    	#puntosP+=1
                    	c.execute('''UPDATE scores
                    					SET score = score + 1
                    					WHERE player = "Purple";'''
                    					)
                        try:
                            pygame.quit()
                        except:
                            if puntosP>puntosY:
                                print('Purple wins!')
                            elif puntosP<puntosY:
                                print('Orange wins!')
                            else:
                                print('Draw!')
                    elif row[-1]=='Y':
                        puntosP = c.execute('SELECT score FROM scores WHERE player = "Purple"')
                		PuntosY = c.execute('SELECT score FROM scores WHERE player = "Orange"')
                    	#puntosY+=1
                    	c.execute('''UPDATE scores
                    					SET score = score + 1
                    					WHERE player = "Orange";'''
                    					)
                        try:
                            pygame.quit()
                        except:
                            if puntosP>puntosY:
                                print('Purple wins!')
                            elif puntosP<puntosY:
                                print('Orange wins!')
                            else:
                                print('Draw!')


                #Verificamos si han pasado 5 minutos.
                if time.time()-timestamp>=300:
                    pygame.quit()
                    

                try:
                    pygame.display.flip()
                except:
                	puntosP = c.execute('SELECT score FROM scores WHERE player = "Purple"')
                	PuntosY = c.execute('SELECT score FROM scores WHERE player = "Orange"')
                    if puntosP>puntosY:
                        print('Purple wins!')
                    elif puntosP<puntosY:
                        print('Orange wins!')
                    else:
                        print('Draw!')   
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_DOWN and Matriz_competicion_4[Prow][Pcolumn] == 'P':
                            if Prow + 1 < rows:
                                if Matriz_competicion_4[Prow + 1][Pcolumn] == True or Matriz_competicion_4[Prow][Pcolumn-1] == "IP":
                                    Matriz_competicion_4[Prow + 1][Pcolumn] = 'P'
                                    Matriz_competicion_4[Prow][Pcolumn] = True
                                    Prow += 1

                        elif event.key == pygame.K_UP and Matriz_competicion_4[Prow][Pcolumn] == 'P':
                            if Prow-1 >= 0:
                                if Matriz_competicion_4[Prow - 1][Pcolumn] == True or Matriz_competicion_4[Prow][Pcolumn-1] == 'IP':
                                    Matriz_competicion_4[Prow - 1][Pcolumn] = 'P'
                                    Matriz_competicion_4[Prow][Pcolumn] = True
                                    Prow -= 1

                        elif event.key == pygame.K_LEFT and Matriz_competicion_4[Prow][Pcolumn] == 'P':
                            if Pcolumn - 1 >= 0:
                                if Matriz_competicion_4[Prow][Pcolumn-1] == True or Matriz_competicion_4[Prow][Pcolumn-1] == 'IP':
                                    Matriz_competicion_4[Prow][Pcolumn-1] = 'P'
                                    Matriz_competicion_4[Prow][Pcolumn] = True
                                    Pcolumn -= 1
                        elif event.key == pygame.K_RIGHT and Matriz_competicion_4[Prow][Pcolumn] == 'P':
                            if Pcolumn + 1 < cols:
                                if Matriz_competicion_4[Prow][Pcolumn + 1] == True or Matriz_competicion_4[Prow][Pcolumn + 1] == 'IP':
                                    Matriz_competicion_4[Prow][Pcolumn+1] = 'P'
                                    Matriz_competicion_4[Prow][Pcolumn] = True
                                    Pcolumn += 1


                        elif event.key == pygame.K_s and Matriz_competicion_4[Yrow][Ycolumn] == 'Y':
                            if Yrow + 1 < rows:
                                if Matriz_competicion_4[Yrow + 1][Ycolumn] == True or Matriz_competicion_4[Yrow][Ycolumn-1] == "IP":
                                    Matriz_competicion_4[Yrow + 1][Ycolumn] = 'Y'
                                    Matriz_competicion_4[Yrow][Ycolumn] = True
                                    Yrow += 1

                        elif event.key == pygame.K_w and Matriz_competicion_4[Yrow][Ycolumn] == 'Y':
                            if Yrow-1 >= 0:
                                if Matriz_competicion_4[Yrow - 1][Ycolumn] == True or Matriz_competicion_4[Yrow][Ycolumn-1] == 'IP':
                                    Matriz_competicion_4[Yrow - 1][Ycolumn] = 'Y'
                                    Matriz_competicion_4[Yrow][Ycolumn] = True
                                    Yrow -= 1

                        elif event.key == pygame.K_a and Matriz_competicion_4[Yrow][Ycolumn] == 'Y':
                            if Ycolumn - 1 >= 0:
                                if Matriz_competicion_4[Yrow][Ycolumn-1] == True or Matriz_competicion_4[Yrow][Ycolumn-1] == 'IP':
                                    Matriz_competicion_4[Yrow][Ycolumn-1] = 'Y'
                                    Matriz_competicion_4[Yrow][Ycolumn] = True
                                    Ycolumn -= 1
                        elif event.key == pygame.K_d and Matriz_competicion_4[Yrow][Ycolumn] == 'Y':
                            if Ycolumn + 1 < cols:
                                if Matriz_competicion_4[Yrow][Ycolumn + 1] == True or Matriz_competicion_4[Yrow][Ycolumn + 1] == 'IP':
                                    Matriz_competicion_4[Yrow][Ycolumn+1] = 'Y'
                                    Matriz_competicion_4[Yrow][Ycolumn] = True
                                    Ycolumn += 1
                        if Matriz_competicion_4[Prow][Pcolumn] == 'P':
                            Matriz_competicion_4 = moverVerdeCompeticion(Gcolumn, Grow, Pcolumn, Prow, Matriz_competicion_4)
                        else:
                            Matriz_competicion_4 = moverVerdeCompeticion(Gcolumn, Grow, Ycolumn, Yrow,Matriz_competicion_4)




                                
