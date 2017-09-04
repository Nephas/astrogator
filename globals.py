import os, sys, time
import pygame as pg
import numpy as np
import random as rd

pg.GAMETIC = 25
pg.RENDER = 26
pg.GUIRENDER = 27
pg.DEBUG = 28
pg.PAUSE = 29

RESOLUTION = [1024,768]

TPS = 30
FPS = 15

R=0; PHI=1
X=0; Y=1
A=0; B=1; TOTAL=2
MIN=0; MAX=1
CLASS = 0; COLOR = 1

GRAV = 2
TRAIL = 1
BODY = 0

SYSTEMSIZE = 100

TRANSPARENCY = pg.Color("white")
TRANSPARENCY.a = 0

def tic():
    return time.time()

def toc(t):
    print((t-time.time())*1000)
