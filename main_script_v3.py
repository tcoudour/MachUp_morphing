from MU_States import *


states1 = MU_States("SingleWingFlapTest.json")

states1.add_states_double([
    {'type':'aero', 'parameter':'alpha', 'final':10, 'points':11}, 
    {'type':'aero', 'parameter':'beta', 'final':10, 'points':11}])
states1.calculate(['aero'])
states1.plot_2D(['alpha', 'beta', 'CL'])

states1.remove_temporary_file()

