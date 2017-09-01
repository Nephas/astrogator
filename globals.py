import os, sys, time
import pygame as pg
import numpy as np
import random as rd
import math
from pygame.locals import *
from Screen import Screen
from Astro import Astro

R=0; PHI=1
X=0; Y=1
A=0; B=1; TOTAL=2
MIN=0; MAX=1
CLASS = 0; COLOR = 1

TRANSPARENCY = pg.Color("white")
TRANSPARENCY.a = 0

def tic():
    return time.time()

def toc(t):
    print((t-time.time())*1000)
