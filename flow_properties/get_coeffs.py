from thermo.chemical import Chemical
from numpy import polyfit, arange
import argparse

class SecondaryProperties:
    """This class calculates the 2nd degree polynomial curve fit for various
    fluid properties. It calculates for a constant pressure over a range of
    temperatures.
    """
    
    def __init__(self, temp, press, fluid):
        """Load temperature range and pressure. Set up flow object with
        fluid.
        """
        self.T_range = arange(temp[0], temp[1])
        self.P = press
        self.tol = Chemical(fluid)

    def thermal_conductivity(self):
        # Thermal Conductivity [W/m-K]
        return self.tol.k
    def rho(self):
        # Density [kg/m^3]
        return self.tol.rho
    def kinematic_viscosity(self):
        # Kinematic Viscosity [kg/m-s]
        return self.tol.mu
    def specific_heat_capacity(self):
        # Specific Heat Capacity [J/kg-K]
        return self.tol.Cp
    def prandtl_number(self):
        # Prandtl Number
        return self.tol.Pr

    def calc_fit(self, property):
        functions = {'k': self.thermal_conductivity,
                     'mu' : self.kinematic_viscosity,
                     'rho' : self.rho,
                     'Cp' : self.specific_heat_capacity,
                     'Pr' : self.prandtl_number}
 
        prop_val = []
        for temp in self.T_range:
            self.tol.calculate(T=temp, P=self.P)
            
            prop_val.append(functions[property]())
        
        res = polyfit(self.T_range, prop_val, 2, full=True)
        print("The fitted curve:")
        print("p(T) = {0}*T**2 + {1}*T + {2}".format(res[0][0], 
                                                     res[0][1], 
                                                     res[0][2]))
        print("Redsiduals")
        print(res[3])

if __name__=='__main__':
    # from command-line argument.
    parser = argparse.ArgumentParser()
    parser.add_argument("T_lower", type=float, help="low T bound")
    parser.add_argument("T_upper", type=float, help="upper T bound")
    parser.add_argument("P", type=float, help="pressure [P]")
    parser.add_argument("prop", type=str, help="flow property")
    parser.add_argument("--fluid", type=str, default='carbon dioxide',
    help="--fluid")

    args = parser.parse_args()

    props = SecondaryProperties((args.T_lower, args.T_upper), args.P, args.fluid)
    props.calc_fit(args.prop)
