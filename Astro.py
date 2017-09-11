"""Author: Marco Fink"""

import numpy as np
import pygame as pg


class Astro:
    """A collection of astrophysical constants and Formulae"""

    G = 0.000296329    # AU^3 d^-2 Mo^-1
    Msol_Me = 333000.  # Mogelfaktor
    Me_Msol = 1 / Msol_Me
    pc_AU = 206264.8    # pc in AU
    AU_pc = 1 / pc_AU
    sigma = 5.67e-08   # W m^-2 K^-4
    Rsol = 695000000   # m
    Lsol = 3.846e26    # Watt
    Msol = 1.988e30    # kg
    rho = 1000        # kg m^-3
    Mearth = 6e24   # kg
    Rearth = 6370000   # m
    AU_kms = 1736.1 # 150000000/(365.25*86400)

    def __init__(self):
        pass

    @staticmethod
    def IMF(m):
        if m < 0.08:
            a = 0.3
        elif m < 0.5:
            a = 1.3
        else:
            a = 2.3
        return m**a

    @staticmethod
    def TitiusBode(i, rin=0.4):       # orbital radius of the i-th planet of the solar system
        return rin + rin * 2**i

    @staticmethod
    def MassLuminosity(M):
        if M < 0.43:
            L = 0.23 * M**2.3
        elif M < 2:
            L = M**4
        elif M < 20:
            L = 1.5 * M**3.5
        else:
            L = 3200 * M
        return L

    @staticmethod
    def MassRadius(M):
        if M < 1:
            R = M**0.6
        else:
            R = M
        return R

    @staticmethod
    def StefanBoltzmann(L, R):  # Temperature of a star
        return ((L * Astro.Lsol) / (4 * np.pi * Astro.sigma * (R * Astro.Rsol)**2))**0.25

    @staticmethod
    def SpectralClass(T):
        if T < 3700:
            SC = "M"
            color = pg.Color("red")
        elif T < 5200:
            SC = "K"
            color = pg.Color("orange")
        elif T < 6000:
            SC = "G"
            color = pg.Color("yellow")
        elif T < 7500:
            SC = "F"
            color = pg.Color("lightyellow")
        elif T < 10000:
            SC = "A"
            color = pg.Color("lightgray")
        elif T < 30000:
            SC = "B"
            color = pg.Color("lightblue")
        else:
            SC = "O"
            color = pg.Color("blue")

        return (SC, color)

    @staticmethod
    def HillSphere(a, m, M):  # two body distance, body mass, parent mass
        return 0.9 * a * (m / (3 * M))**(0.333)

    @staticmethod
    def PlanetRadius(M):
        return 1. / Astro.Rearth * ((3. * M * Astro.Mearth) / (4. * np.pi * Astro.rho))**(0.333)

    @staticmethod
    def vOrbit(r, M):  # in AU/day
        tOrb = 365 * np.sqrt(r**3 / M)
        return 2*np.pi*r/tOrb
