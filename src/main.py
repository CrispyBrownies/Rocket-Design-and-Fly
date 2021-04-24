# Stephen Chen
# MAE423: Intro to Propulsion
# Created: 4/23/2021

import math

# Defining inputs
Ml = 5  # Payload Mass [kg]
ps = 1820  # Shell Density (carbon-epoxy) [1kg/m^3]
pp = 1772  # Propellant Density (66 − 78% AP, 18% organic polymer, 4 − 20% Al) [kg/m^3]
sigs = 80  # Shell Working Stress [MPa]
N = 4  # Number of fins
hmaxList = [10000, 20000, 30000]  # Maximum Altitude [ft]
amaxList = [5, 10, 20]  # Normalized Max Acceleration
SMList = [1, 2, 3]  # Static Margin (Xcp-Xcg)/D
g = 9.81  # Acceleration due to Gravity [m/s^2]


# Step 1
def Eq1(hmax, amax):  # returns: [ropt, weq, tb]
    ropt = amax + 1
    weq = math.sqrt((hmax * g) / ((math.log(ropt) / 2) * (math.log(ropt) - 2) + ((ropt - 1) / ropt)))
    tb = ((ropt - 1) * weq) / (g * ropt)
    return [ropt, weq, tb]


def Eq2(inputs):
    return []
