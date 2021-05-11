# Stephen Chen
# MAE423: Intro to Propulsion
# Created: 4/23/2021

import math
# import plotly.graphic_objects as go

# Defining inputs
Ml = 5  # Payload Mass [kg]
ps = 1820  # Shell Density (carbon-epoxy) [1kg/m^3]
pp = 1772  # Propellant Density (66 − 78% AP, 18% organic polymer, 4 − 20% Al) [kg/m^3]
sigs = 80000000  # Shell Working Stress [Pa]
N = 4  # Number of fins
hmaxList = [6096]  #[3048, 6096, 9144]  # Maximum Altitude [m] (10k, 20k, 30k ft)
amaxList = [10]  # [5, 10, 20]  # Normalized Max Acceleration
SMList = [2]  #[1, 2, 3]  # Static Margin (Xcp-Xcg)/D
g = 9.81  # Acceleration due to Gravity [m/s^2]

# Defining constants
gamma = 1.4  #
pa = 101325  # Atmospheric pressure [Pa]
a = 346      # Speed of sound at sea-level [m/s]

rocketList = []
lambdas = []
newRockets = []


class Rocket():
    def __init__(self, h, a, sm):
        self.hmax = h
        self.amax = a
        self.SM = sm
        self.CGmatch = False
        self.deltaD = 0.001
        self.deltaL = 0.001
        self.tol = 10**-5
        self.lMax = 5  # Max length of rocket [m]
        self.dMax = 3  # Max diameter of rocket [m]
        self.lambdaMax = 0
        self.e = 0
        self.mdot = 0
        self.thrust = 0
        self.ropt, self.weq, self.tb, self.Meq, self.p0, self.delta, self.d, self.l, self.Xcp, self.Xcg, self.lambd, self.Mp, self.Ms, self.Lp = 0, 0, 0, 0, 0, 0, 0.001, 0.001, 0, 0, 0, 0, 0, 0

    def __str__(self):
        return "lambda: "+ str(self.lambd) + " d: " + str(self.d) + " l: " + str(self.l) + " delta: "+str(self.delta) + " Ms: "+str(self.Ms) + " Mp: "+str(self.Mp) + '\n' \
               + " Lp: "+str(self.Lp) + " Xcg: " + str(self.Xcg) + " Xcp: " + str(self.Xcp) + " Ropt: " + str(self.ropt) + " Weq: " + str(self.weq) + " tb:" + str(self.tb) + '\n' \
                + " P0/Pa" + str(self.p0/pa) + " e: " + str(self.e) + " hmax: " + str(self.hmax) + " amax: " + str(self.amax) + " SM: " + str(self.SM) + " T: " + str(self.thrust)

    # Step 1, calculate Ropt, Wep, tb, P0
    def Eq1(self):  # returns: [ropt, weq, tb]
        self.ropt = self.amax + 1
        self.weq = math.sqrt((self.hmax * g) / ((math.log(self.ropt) / 2) * (math.log(self.ropt) - 2) + ((self.ropt - 1) / self.ropt)))
        self.tb = ((self.ropt - 1) * self.weq) / (g * self.ropt)
        self.Meq = self.weq / a
        self.p0 =  pa / ((1 + (gamma - 1) * 0.5 * self.Meq ** 2) ** (-gamma / (gamma - 1)))
        # return [ropt, weq, tb, p0]

    # Step 2, after guess D and L, calculate Ms, Mp, Lp, Xcp, Xcg
    def Eq2(self):
        self.delta = self.d * self.p0 / (2 * sigs)  # Thickness of the shell due to material limitations

        # Calculating mass of the rocket (shell and propellant)
        SAbody = math.pi * self.d * (self.l + self.d)  # Surface area of the body tube
        Afin = 0.5 * (self.d ** 2)  # Cross-sectional area of one fin
        SAcone = 0.5 * math.pi * self.d * (0.5 * self.d + math.sqrt(self.d ** 2 + 0.25 * self.d ** 2))  # Surface area of the rocket cone

        Msbody = SAbody * self.delta * ps  # Assuming cylindrical shell and shell thickness << diameter
        Msfin = Afin * self.delta * ps  # Assuming fin thickness is equal to shell thickness
        Mscone = SAcone * self.delta * ps  # Calculated using surface area of cone

        self.Ms = Msbody + N * Msfin + Mscone  # Total mass of the rocket shell
        self.Mp = (self.ropt - 1) * (self.Ms + Ml)  # Mass of propellant
        self.Lp = self.Mp / (math.pi * self.d * self.d * pp * 0.25)  # Length of the propellant tube

        # Calculating Xcp
        # For nose cone
        Cncone = 2
        xconebar = (2/3)*self.d

        # For fin
        a = self.d
        m = self.d
        b = 0
        l = math.sqrt((0.5*self.d)**2+self.d**2)
        s = self.d
        Cnfin = (4*N*(s/self.d)**2)/(1+math.sqrt(1+((2*l)/(a+b))**2))
        xfbar = self.l+self.d+(m*(a+2*b))/(3*(a+b))+(1/6)*(a+b-(a*b)/(a+b))
        kfb = 1+(self.d/2)/s+(self.d/2)
        Cnfinb = Cnfin*kfb

        self.Xcp = (Cncone*xconebar+Cnfinb*xfbar)/(Cncone+Cnfinb)

        # Calculating Xcg
        mcg = (Mscone + Ml) * (2 / 3) * self.d + Msbody * (self.d + (self.l + self.d) * 0.5) + self.Mp * ((2 * self.d + self.l) - 0.5 * self.Lp) + N * Msfin * (
                    self.d + self.l + (2 / 3) * self.d)
        # print(mcg)
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
        if abs(self.Xcp - self.Xcg - self.d * self.SM) < self.tol:
            return True
        else:
            return False

    def CalcLambda(self):
        self.lambd = round(Ml / (self.Mp + self.Ms), 6)
        self.e = round(self.Ms/(self.Ms+self.Mp), 6)
        self.mdot = self.Mp/self.tb
        self.thrust = self.weq*self.mdot

    def LpValid(self):
        if self.Lp > self.l+self.d:
            return False
        else:
            return True


# Creates 27 different rockets with different input parameters
def CreateRockets27():
    for h in hmaxList:
        for amax in amaxList:
            for sm in SMList:
                rocket = Rocket(h, amax, sm)
                rocket.Eq1()
                rocketList.append(rocket)


# Creates 9 rockets by using medium value for unfocused parameters
def CreateRockets9():
    for h in hmaxList:
        rocket = Rocket(h, amaxList[1], SMList[1])
        rocket.Eq1()
        rocketList.append(rocket)

    for amax in amaxList:
        rocket = Rocket(hmaxList[1], amax, SMList[1])
        rocket.Eq1()
        rocketList.append(rocket)

    for sm in SMList:
        rocket = Rocket(hmaxList[1], amaxList[1], sm)
        rocket.Eq1()
        rocketList.append(rocket)


# Iteratively configures the rocket's size
def ConfigureRockets():
    global newRockets
    for rocket in rocketList:
        print("Testing rocket for hmax = " + str(rocket.hmax) + ", amax = " + str(rocket.amax) + ", SM = " + str(rocket.SM))
        validRockets = {}
        bestLambda = 0
        while not (rocket.CheckMaxD() and rocket.CheckMaxL()):
            rocket.Eq2()
            if rocket.LpValid():
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
        validMax = max(validRockets.keys())
        (maxl, maxd) = validRockets[validMax]
        newRock = Rocket(rocket.hmax, rocket.amax, rocket.SM)
        newRock.l = maxl
        newRock.d = maxd
        newRock.Eq1()
        newRock.Eq2()
        newRock.CalcLambda()
        newRockets.append(newRock)


# def CreateTable(rocketList):
#     fig = go.Figure(data=[go.Table(
#         header = dict(values=['Cases', 'Ropt', 'Weq', 'tb', 'p0/pa', 'delta/D', 'D', 'L/D', 'Xcg', 'Xcp', 'Mp', 'Ms', 'Mo', 'lambda', 'e'])
#     )])


CreateRockets9()
ConfigureRockets()

print(lambdas)
print(len(lambdas))
print(max(lambdas))
for each in newRockets:
    print(each)
    print('')


# rocket = Rocket(3048, 6, 1)
# rocket.Eq1()
# rocket.l, rocket.d = 2.7, .5
# rocket.Eq2()
# rocket.CalcLambda()
# print(rocket)
# print(rocket.Xcg)
# print(rocket.Xcp)