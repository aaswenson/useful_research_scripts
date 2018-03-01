from thermo.chemical import Chemical

class SecondaryProperties:

    def __init__(self, temp, press):

        self.T_range = temp
        self.P = press
        self.tol = Chemical('carbon dioxide')

    def thermal_conductivity(self):
        return self.tol.k
    def rho(self):
        return self.tol.rho
    def kinematic_viscosity(self):
        return self.tol.mu
    def specific_heat_capacity(self):
        return self.tol.Cp
    def prandtl_number(self):
        return self.tol.Pr

    def calc_fit(self, property):

        functions = {'k': self.thermal_conductivity,
                     'mu' : self.kinematic_viscosity,
                     'rho' : self.rho,
                     'Cp' : self.specific_heat_capacity,
                     'Pr' : self.prandtl_number}
        prop_val = []
        for temp in range(self.T_range[0], self.T_range[1], 1):
            self.tol.calculate(T=temp, P=self.P)
            
            prop_val.append(functions[property]())
        
        return prop_val



test = SecondaryProperties((900, 1100), 1.7e7)
testval = test.calc_fit('k')
print(testval)
