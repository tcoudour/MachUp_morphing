from __future__ import print_function
import machup.MU as MU
import numpy as np
import matplotlib.pyplot as plt
import json
from collections import OrderedDict
import time
from shutil import copy 
from os import remove, rename
# from sys import stdout


filename = "SingleWingFlap.json" # input file
temp_filename = "temp_data.json" # name for a copy of the input file that will be modified if necessary.
copy(filename, temp_filename) # copy input file

muAirplane = MU.MachUp(temp_filename)

long_ref = muAirplane.myairplane.get_long_ref()
lat_ref = muAirplane.myairplane.get_lat_ref()
area = long_ref * lat_ref

all_results = []
calc_stall_angle = False
calc_stall_speed = False
weight = 10000 # Weight in Newtons


#Default aero parameters
aileron_def = 0
elevator_def = 0
rudder_def = 0
flap_def = 0
V_def = 10
alpha_def = 0
beta_def = 0
rho_def = 0.0023769

def solve_once(param = None, value = None):

	values_dict = {
		"aileron": aileron_def,
		"elevator": elevator_def,
		"rudder": rudder_def,
		"flap": flap_def,
		"V_mag": V_def,
		"alpha": alpha_def,
		"beta": beta_def,
		"rho": rho_def
	}
	if param is not None and value is not None :
		values_dict[param] = value
	
	control_state = {
		"aileron": values_dict['aileron'],
		"elevator": values_dict['elevator'],
		"rudder": values_dict['rudder'],
		"flap": values_dict['flap']
	}
	aero_state = {
		"V_mag": values_dict['V_mag'],
		"alpha": values_dict['alpha'],
		"beta": values_dict['beta'],
		"rho": values_dict['rho']
	}
	#prop_state = {"J": 0.25}

	
	results = muAirplane.solve(aero_state = aero_state,
							   control_state = control_state,
							   # prop_state = prop_state,
							   # filename = 'results1.json' # output file
							   ) 

	# Calculate Lift and Drag coefficients
	results['CL'] = (2*results['FL'])/(aero_state['rho']*(aero_state['V_mag']**2)*area)
	results['CD'] = (2*results['FD'])/(aero_state['rho']*(aero_state['V_mag']**2)*area)
	results['L/D'] = results['CL'] / results['CD']
		
	# Save parameters with results
	results['AILERON'] = control_state['aileron']
	results['ELEVATOR'] = control_state['elevator']
	results['RUDDER'] = control_state['rudder']
	results['FLAP'] = control_state['flap']
	
	results['V_MAG'] = aero_state['V_mag']
	results['ALPHA'] = aero_state['alpha']
	results['BETA'] = aero_state['beta']
	results['RHO'] = aero_state['rho']
	
	# Save wing geometry
	results['SWEEP'] = muAirplane.myairplane._wings['Wing_1']._left_segment._dimensions['sweep']
	results['SPAN'] = muAirplane.myairplane._wings['Wing_1']._left_segment._dimensions['span']
	results['DIHEDRAL'] = muAirplane.myairplane._wings['Wing_1']._left_segment._dimensions['dihedral']
	results['TIP_CHORD'] = muAirplane.myairplane._wings['Wing_1']._left_segment._dimensions['tip_chord']
	results['MOUNTING_ANGLE'] = muAirplane.myairplane._wings['Wing_1']._left_segment._dimensions['mounting_angle']
	results['WASHOUT'] = muAirplane.myairplane._wings['Wing_1']._left_segment._dimensions['washout']
	results['ROOT_CHORD'] = muAirplane.myairplane._wings['Wing_1']._left_segment._dimensions['root_chord']
	results['YOFFSET'] = muAirplane.myairplane._wings['Wing_1']._left_segment._dimensions['yoffset']
	results['CHORD'] = muAirplane.myairplane._wings['Wing_1']._left_segment._dimensions['root_chord']
	
	# Save airfoil data
	results['ALPHA_L0'] = muAirplane.myairplane._wings['Wing_1'].airfoil(0)._properties['alpha_L0']
	results['CL_ALPHA'] = muAirplane.myairplane._wings['Wing_1'].airfoil(0)._properties['CL_alpha']
	results['CM_L0'] = muAirplane.myairplane._wings['Wing_1'].airfoil(0)._properties['Cm_L0']
	results['CM_ALPHA'] = muAirplane.myairplane._wings['Wing_1'].airfoil(0)._properties['Cm_alpha']
	results['CD0'] = muAirplane.myairplane._wings['Wing_1'].airfoil(0)._properties['CD_0']
	results['CD0_L'] = muAirplane.myairplane._wings['Wing_1'].airfoil(0)._properties['CD_L']
	results['CD0_L2'] = muAirplane.myairplane._wings['Wing_1'].airfoil(0)._properties['CD_L2']
	results['CL_MAX'] = muAirplane.myairplane._wings['Wing_1'].airfoil(0)._properties['CL_max']
	
	# Others
	if calc_stall_angle : #Only calculate stall angle if studied since it takes time
		results['STALL_ANGLE'] = muAirplane.stall_onset(aero_state=aero_state, control_state=control_state)['alpha']
		results['STALL_LIFT'] = muAirplane.stall_onset(aero_state=aero_state, control_state=control_state)['lift']
	if calc_stall_speed : #Only calculate stall angle if studied since it takes time
		results['STALL_SPEED'] = muAirplane.stall_airspeed(weight=weight, aero_state=aero_state, control_state=control_state)
	
	return results # Contains FL, FD, FS, FX, FY, FZ, MX, MY, MZ; CL, CD, L/D; control parameters, aero parameters, wing geometry, airfoil

def update_geometry(param, value) : #Modifies the .json input file to change the geometry
	global muAirplane
	if not (param in ['sweep', 'span', 'dihedral', 'tip_chord', 'mounting_angle', 'washout', 'root_chord', 'yoffset', 'chord']) :
		exit('Wrong parameter name (at update_geometry)')
	with open(temp_filename, 'r+') as f :
		data = json.load(f, object_pairs_hook=OrderedDict)
		if param == 'chord' :
			data['wings']['Wing_1']['root_chord'] = value
			data['wings']['Wing_1']['tip_chord'] = value
		else :
			data['wings']['Wing_1'][param] = value
		f.seek(0)
		json.dump(data, f, indent=4)
		f.truncate()
	muAirplane = MU.MachUp(temp_filename)
	return 0

def update_airfoil(param, value) : #Modifies the .json input file to change the airfoil
	global muAirplane
	if not (param in ['alpha_L0', 'CL_alpha', 'Cm_L0', 'Cm_alpha', 'CD0', 'CD0_L', 'CD0_L2', 'CL_max']) :
		exit('Wrong parameter name (at update_airfoil)')
	with open(temp_filename, 'r+') as f :
		data = json.load(f, object_pairs_hook=OrderedDict)
		data['wings']['Wing_1']['airfoils']['af1']['properties'][param] = value
		data['wings']['Wing_1']['airfoils']['af2']['properties'][param] = value
		f.seek(0)
		json.dump(data, f, indent=4)
		f.truncate()
	muAirplane = MU.MachUp(temp_filename)
	return 0


def solve_all(param, min, max, points):
	global all_results
	
	if not (param in ['aileron', 'elevator', 'rudder', 'flap', 'V_mag', 'alpha', 'beta', 'rho', 
					'sweep', 'span', 'dihedral', 'tip_chord', 'mounting_angle', 'washout', 'root_chord', 'yoffset', 'chord',
					'alpha_L0', 'CL_alpha', 'Cm_L0', 'Cm_alpha', 'CD0', 'CD0_L', 'CD0_L2', 'CL_max']) :
		exit('Wrong parameter name (at solve_all)')
		
	solve_results = []
	values_list = np.linspace(min, max, points)
	time_begin = time.time()
	for i in values_list :
		if param in ['aileron', 'elevator', 'rudder', 'flap', 'V_mag', 'alpha', 'beta', 'rho'] :
			solve_results.append(solve_once(param, i))
		if param in ['sweep', 'span', 'dihedral', 'tip_chord', 'mounting_angle', 'washout', 'root_chord', 'yoffset', 'chord'] :
			update_geometry(param, i)
			solve_results.append(solve_once())
		if param in ['alpha_L0', 'CL_alpha', 'Cm_L0', 'Cm_alpha', 'CD0', 'CD0_L', 'CD0_L2', 'CL_max'] :
			update_airfoil(param, i)
			solve_results.append(solve_once())
		solve_results[-1]['value'] = i
		progress = round(len(solve_results)*100/points, 1)
		print('['+'#'*int(progress/10)+'-'*(10-int((progress/10)))+'] ' + format(int(progress), '02d') + '% in ' + str(round(time.time()-time_begin, 1)) + ' s', end = '\r')
	return solve_results

def units(data) :
	if data in ['AILERON', 'ELEVATOR', 'RUDDER', 'FLAP', 'ALPHA', 'BETA', 'SWEEP', 'DIHEDRAL', 'MOUNTING_ANGLE', 'WASHOUT', 'STALL_ANGLE'] :
		return ' [deg]'
	elif data in ['alpha_L0'] :
		return ' [rad]'
	elif data in ['CL_alpha', 'CM_alpha'] :
		return ' [1/rad]'
	else :
		return ''


def plot_data(data): # prints a plot of a list of data against another (['CL', 'alpha'] gives CL against alpha)
	i = 1
	for d in data:
		d[0] = d[0].upper() #uppercase
		d[1] = d[1].upper()
		if not(d[0] in all_results[0]):
			exit('Unable to find data with the name "' + d[0] + '" in results')
		if not(d[1] in all_results[0]):
			exit('Unable to find data with the name "' + d[1] + '" in results')
			
		list_data_x = []
		list_data_y = []
		for j in range(len(all_results)):
			list_data_y.append(all_results[j][d[0]])
			# list_data_x.append(all_results[j][d[1]])
			list_data_x.append(all_results[j]['value'])
		
		plt.figure(i)
		i = i+1
		plt.plot(list_data_x, list_data_y)
		plt.xlabel(d[1] + units(d[1]))
		plt.ylabel(d[0] + units(d[0]))
		plt.title(d[0] + ' against ' + d[1] + ', ' + str(len(list_data_x)) + ' points from ' + str(min(list_data_x)) + ' to ' + str(max(list_data_x)))
		plt.grid(True)
	plt.show()
	return 0

def study(param, points, data): #Calculates and display results for chosen parameter
	'''
	"param" is a list containing parameters
	each parameter is a list containing the name of the parameter, the minimum, and the maximum values
	"points" is the number of values to calculate(precision)
	"data is a list containing the names of the results to display
	
	Parameters can be :
		Aero parameters : 'aileron', 'elevator', 'rudder', 'flap', 'V_mag', 'alpha', 'beta', 'rho'
		Geometry parameters : 'sweep', 'span', 'dihedral', 'tip_chord', 'mounting_angle', 'washout', 'root_chord', 'yoffset'
		Airfoil parameters : 'alpha_L0', 'CL_alpha', 'Cm_L0', 'Cm_alpha', 'CD0', 'CD0_L', 'CD0_L2', 'CL_max'
	Data can be : 'CL', 'CD', 'L/D', 'FL', 'FD', 'FS', 'FX', 'FY', 'FZ', 'MX', 'MY', 'MZ', 
					'STALL_ANGLE', 'STALL_SPEED' (Calculations get much longer)
	'''
	global calc_stall_angle
	global calc_stall_speed
	global all_results
	
	time_start = time.time()
	calc_stall_angle = False
	if 'STALL_ANGLE' in data or 'STALL_LIFT' in data : #Only calculate stall angles if studied
		calc_stall_angle = True
	calc_stall_speed = False
	if 'STALL_SPEED' in data :
		calc_stall_speed = True
	
	if len(param) == 1 :
		all_results = solve_all(param[0][0], param[0][1], param[0][2], points)
		plots_list = []
		for d in data :
			plots_list.append([d, param[0][0]])
		print (' '*100, end = '\r')
		print ('Study finished in ' + str(round(time.time()-time_start, 1)) + ' seconds')
		plot_data(plots_list)
	else :
		exit('Too many parameters')


study([['CL_alpha', 0, 50]], 50 , ['STALL_ANGLE'])

# ''' TESTING '''
# control_state = {"aileron": aileron_def, "elevator": elevator_def, "rudder": rudder_def, "flap": 0}
# aero_state = {"V_mag": V_def, "alpha": alpha_def, "beta": beta_def, "rho": rho_def}
# for k in range(10) :
	# control_state['flap'] = k
	# stalling = muAirplane.stall_onset(aero_state=aero_state, control_state=control_state)
	# print (str(stalling['alpha']) + ', ' + str(stalling['lift']))

remove(temp_filename) # Remove temporary file