# Stephen Chen
# MAE423: Intro to Propulsion
# Created: 4/23/2021

import math

# Defining inputs
Ml = 5  # Payload Mass [kg]
ps = 1820  # Shell Density (carbon-epoxy) [1kg/m^3]
pp = 1772  # Propellant Density (66 − 78% AP, 18% organic polymer, 4 − 20% Al) [kg/m^3]
sigs = 80000000  # Shell Working Stress [Pa]
N = 4  # Number of fins
hmaxList = [3048, 6096, 9144]  # Maximum Altitude [m] (10k, 20k, 30k ft)
amaxList = [5, 10, 20]  # Normalized Max Acceleration
SMList = [1, 2, 3]  # Static Margin (Xcp-Xcg)/D
g = 9.81  # Acceleration due to Gravity [m/s^2]

# Defining constants
gamma = 1.4  #
pa = 101325  # Atmospheric pressure [Pa]
a = 344      # Speed of sound at sea-level [m/s]

rocketList = []

class Rocket():
    def __init__(self, h, a, sm):
        self.hmax = h
        self.amax = a
        self.SM = sm
        self.CGmatch = False
        self.deltaD = 0.01
        self.deltaL = 0.01
        self.ropt, self.weq, self.tb, self.Meq, self.p0, self.delta, self.d, self.l, self.Xcp, self.Xcg = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0

    # Step 1, calculate Ropt, Wep, tb, P0
    def Eq1(self):  # returns: [ropt, weq, tb]
        self.ropt = self.amax + 1
        self.weq = math.sqrt((self.hmax * g) / ((math.log(self.ropt) / 2) * (math.log(self.ropt) - 2) + ((self.ropt - 1) / self.ropt)))
        self.tb = ((self.ropt - 1) * self.weq) / (g * self.ropt)
        self.Meq = self.weq / a
        self.p0 = (1 + (gamma - 1) * self.Meq ** 2 * 0.5) ** (gamma / (gamma - 1)) * pa
        # return [ropt, weq, tb, p0]

    # Step 2, after guess D and L, calculate Ms, Mp, Lp, Xcp, Xcg
    def Eq2(self):
        self.delta = self.d * self.p0 / (2 * sigs)  # Thickness of the shell due to material limitations

        # Calculating mass of the rocket (shell and propellant)
        SAbody = math.pi * self.d * self.l  # Surface area of the body tube
        Afin = 0.5 * (self.d ** 2)  # Cross-sectional area of one fin
        SAcone = 0.5 * math.pi * self.d * (0.5 * self.d + math.sqrt(self.d ** 2 + 0.25 * self.d ** 2))  # Surface area of the rocket cone

        Msbody = SAbody * self.delta * ps  # Assuming cylindrical shell and shell thickness << diameter
        Msfin = Afin * self.delta * ps  # Assuming fin thickness is equal to shell thickness
        Mscone = SAcone * self.delta * ps  # Calculated using surface area of cone

        Ms = Msbody + N * Msfin + Mscone  # Total mass of the rocket shell
        Mp = (self.ropt - 1) * (Ms + Ml)  # Mass of propellant
        Lp = Mp / (math.pi * self.d * self.d * pp * 0.25)  # Length of the propellant tube

        # Calculating Xcp, using 2D assumption
        Abody = self.d * self.l
        Acone = self.d * self.d * 0.5
        Atotal = Abody + Acone + 2 * Afin

        cpa = Acone * (2 / 3) * self.d + Abody * (self.d + 0.5 * (self.l + self.d)) + (2 * Afin) * (self.d + self.l + (2 / 3) * self.d)
        self.Xcp = cpa / Atotal

        # Calculating Xcg
        mcg = (Mscone + Ml) * (2 / 3) * self.d + Msbody * (self.d + self.l * 0.5) + Mp * ((2 * self.d + self.l) - 0.5 * Lp) + N * Msfin * (
                    self.d + self.l + (2 / 3) * self.d)
        self.Xcg = mcg / (Ms + Ml + Mp)
        # return [Xcp, Xcg]

    def UpdateD(self):
        self.d += self.deltaD

    def UpdateL(self):
        self.l += self.deltaL

    def ResetL(self):
        self.l = 0


# Creates different rockets with different input parameters
def CreateRockets():
    for h in hmaxList:
        for amax in amaxList:
            for sm in SMList:
                rocket = Rocket(h, amax, sm)
                rocket.Eq1()
                rocketList.append(rocket)


# Iteratively configures the rocket's size
def ConfigureRockets():
    for rocket in rocketList:
        if rocket.CGmatch:
            if rocket.lambdaMatch:
                pass  # success
            else:
                rocket.resetL()
                rocket.UpdateD()
                rocket.Eq2()
        else:
            rocket.UpdateL()
            rocket.Eq2()


