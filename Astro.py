from globals import *

class Astro:
    G = 0.000296329    # AU^3 d^-2 Mo^-1
    Msol_Me = 333000./10000 # Mogelfaktor
    Me_Msol = 1/Msol_Me
    sigma = 5.67e-08   # W m^-2 K^-4
    Rsol = 695000000   # m
    Lsol = 3.846e26    # Watt
    Msol = 1.988e30    # kg
    rho  = 1000        # kg m^-3
    Mearth = 6e24   # kg
    Rearth = 6370000   # m
    def __init__(self):
        return

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
    def TitiusBode(i):       # orbital radius of the i-th planet of the solar system
        return 0.4 + 0.3*2**i

    @staticmethod
    def MassLuminosity(M):
        if M < 0.43:
            L = 0.23*M**2.3
        elif M < 2:
            L = M**4
        elif M < 20:
            L = 1.5*M**3.5
        else:
            L = 3200*M
        return L

    @staticmethod
    def MassRadius(M):
        if M < 1:
            R = M**0.6
        else:
            R = M
        return R

    @staticmethod
    def StefanBoltzmann(L,R):  # Temperature of a star
        return ((L*Astro.Lsol)/(4*math.pi*Astro.sigma*(R*Astro.Rsol)**2))**0.25

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
            color = pg.Color("white")
        elif T < 30000:
            SC = "B"
            color = pg.Color("lightblue")
        else:
            SC = "O"
            color = pg.Color("blue")

        return [SC, color]

    @staticmethod
    def HillSphere(a,m,M): # two body distance, body mass, parent mass
        return a*(m/(3*M))**(0.333)

    @staticmethod
    def PlanetRadius(M):
        return 1./Astro.Rearth*((3.*M*Astro.Mearth)/(4.*math.pi*Astro.rho))**(0.333)
