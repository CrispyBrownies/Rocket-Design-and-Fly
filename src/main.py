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
hmaxList = [3048] #, 6096, 9144]  # Maximum Altitude [m] (10k, 20k, 30k ft)
amaxList = [5] #, 10, 20]  # Normalized Max Acceleration
SMList = [1] #, 2, 3]  # Static Margin (Xcp-Xcg)/D
g = 9.81  # Acceleration due to Gravity [m/s^2]

# Defining constants
gamma = 1.4  #
pa = 101325  # Atmospheric pressure [Pa]
a = 346      # Speed of sound at sea-level [m/s]

rocketList = []
lambdas = []


class Rocket():
    def __init__(self, h, a, sm):
        self.hmax = h
        self.amax = a
        self.SM = sm
        self.CGmatch = False
        self.deltaD = 0.01
        self.deltaL = 0.01
        self.tol = 10**-5
        self.lMax = 10  # Max length of rocket [m]
        self.dMax = 5  # Max diameter of rocket [m]
        self.lambdaMax = 0
        self.ropt, self.weq, self.tb, self.Meq, self.p0, self.delta, self.d, self.l, self.Xcp, self.Xcg, self.lambd, self.Mp, self.Ms, self.Lp = 0, 0, 0, 0, 0, 0, 0.01, 0.01, 0, 0, 0, 0, 0, 0

    def __str__(self):
        return "lambda: "+ str(self.lambd) + " d: " + str(self.d) + " l: " + str(self.l) + " delta: "+str(self.delta)

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

        self.Ms = Msbody + N * Msfin + Mscone  # Total mass of the rocket shell
        self.Mp = (self.ropt - 1) * (self.Ms + Ml)  # Mass of propellant
        self.Lp = self.Mp / (math.pi * self.d * self.d * pp * 0.25)  # Length of the propellant tube

        # Calculating Xcp, using 2D assumption
        Abody = self.d * self.l
        Acone = self.d * self.d * 0.5
        Atotal = Abody + Acone + 2 * Afin

        cpa = Acone * (2 / 3) * self.d + Abody * (self.d + 0.5 * (self.l + self.d)) + (2 * Afin) * (self.d + self.l + (2 / 3) * self.d)
        self.Xcp = cpa / Atotal

        # Calculating Xcg
        mcg = (Mscone + Ml) * (2 / 3) * self.d + Msbody * (self.d + self.l * 0.5) + self.Mp * ((2 * self.d + self.l) - 0.5 * self.Lp) + N * Msfin * (
                    self.d + self.l + (2 / 3) * self.d)
        self.Xcg = mcg / (self.Ms + Ml + self.Mp)
        # return [Xcp, Xcg]

    def UpdateD(self):
        self.d += self.deltaD

    def UpdateL(self):
        self.l += self.deltaL

    def ResetL(self):
        self.l = 0.01

    def CheckMaxD(self):
        if self.d < self.dMax:
            return False
        else:
            return True

    def CheckMaxL(self):
        if self.l < self.lMax:
            return False
        else:
            return True

    def CheckCGMatch(self):
        if self.Xcp - self.Xcg - self.d * self.SM < self.tol:
            return True
        else:
            return False

    def CalcLambda(self):
        self.lambd = round(Ml / (self.Mp + self.Ms), 6)


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
        validRockets = {}
        bestLambda = 0
        # bestRocket = Rocket(0, 0, 0)
        while not (rocket.CheckMaxD() and rocket.CheckMaxL()):
            # print(rocket.l)
            rocket.Eq2()
            if rocket.CheckCGMatch():
                rocket.CalcLambda()
                lambdas.append(rocket.lambd)
                if rocket.lambd > bestLambda:
                    validRockets[rocket.lambd] = (rocket.l, rocket.d)
                    bestLambda = rocket.lambd
            if not rocket.CheckMaxL():
                rocket.UpdateL()
            else:
                rocket.ResetL()
                rocket.UpdateD()
        print(validRockets)
        validMax = max(validRockets.keys())
        print(validMax)
        print(validRockets[validMax])
        return validRockets[validMax]

        # for rock in validRockets.values():
        #     print(rock)


# CreateRockets()
# rocketParam = ConfigureRockets()
rocket = Rocket(3048, 6, 1)
rocket.Eq1()
print(rocket.tb)
# rocket.l = rocketParam[0]
# rocket.d = rocketParam[1]
# rocket.Eq1()
# rocket.Eq2()
# print(rocket)
# # print(lambdas)
# print(len(lambdas))
# print(max(lambdas))

