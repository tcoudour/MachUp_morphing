'''
Script now obsolete, use main_script_v2.py instead
'''

from __future__ import print_function
import machup.MU as MU
import numpy as np
import matplotlib.pyplot as plt
import json
from collections import OrderedDict
import time
from shutil import copy 
from os import remove, rename


# filename = "SingleWingFlapTest.json" # input file
filename = "TwoWings.json" # input file
temp_filename = "temp_data.json" # name for a copy of the input file that will be modified if necessary.
copy(filename, temp_filename) # copy input file

muAirplane = MU.MachUp(temp_filename)

long_ref = muAirplane.myairplane.get_long_ref()
lat_ref = muAirplane.myairplane.get_lat_ref()
area = long_ref * lat_ref

all_results = []
calc_stall_angle = False
calc_stall_speed = False
calc_stall_points = False
weight = 10000 # Weight in Newtons for stall speed calculation


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
		"AILERON": aileron_def,
		"ELEVATOR": elevator_def,
		"RUDDER": rudder_def,
		"FLAP": flap_def,
		"V_MAG": V_def,
		"ALPHA": alpha_def,
		"BETA": beta_def,
		"RHO": rho_def
	}
	if param is not None and value is not None :
		values_dict[param] = value
	
	control_state = {
		"aileron": values_dict['AILERON'],
		"elevator": values_dict['ELEVATOR'],
		"rudder": values_dict['RUDDER'],
		"flap": values_dict['FLAP']
	}
	aero_state = {
		"V_mag": values_dict['V_MAG'],
		"alpha": values_dict['ALPHA'],
		"beta": values_dict['BETA'],
		"rho": values_dict['RHO']
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
	if calc_stall_angle or calc_stall_points: #Only calculate stall angle if studied since it takes time
		results['STALL_ANGLE'] = muAirplane.stall_onset(aero_state=aero_state, control_state=control_state)['alpha']
		results['STALL_LIFT'] = muAirplane.stall_onset(aero_state=aero_state, control_state=control_state)['lift']
		results['STALLING'] = (results['ALPHA'] >= results['STALL_ANGLE'])
	if calc_stall_speed : #Only calculate stall angle if studied since it takes time
		results['STALL_SPEED'] = muAirplane.stall_airspeed(weight=weight, aero_state=aero_state, control_state=control_state)

	
	return results # Contains FL, FD, FS, FX, FY, FZ, MX, MY, MZ; CL, CD, L/D; control parameters, aero parameters, wing geometry, airfoil

def update_geometry(param, value) : #Modifies the .json input file to change the geometry
	global muAirplane
	if not (param in ['SWEEP', 'SPAN', 'DIHEDRAL', 'TIP_CHORD', 'MOUNTING_ANGLE', 'WASHOUT', 'ROOT_CHORD', 'YOFFSET', 'CHORD']) :
		exit('Wrong parameter name ' + param + ' (at update_geometry)')
	with open(temp_filename, 'r+') as f :
		data = json.load(f, object_pairs_hook=OrderedDict)
		if param == 'CHORD' :
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
	if not (param in ['ALPHA_L0', 'CL_ALPHA', 'CM_L0', 'CM_ALPHA', 'CD0', 'CD0_L', 'CD0_L2', 'CL_MAX']) :
		exit('Wrong parameter name ' + param + ' (at update_airfoil)')
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
	
	if not (param in ['AILERON', 'ELEVATOR', 'RUDDER', 'FLAP', 'V_MAG', 'ALPHA', 'BETA', 'RHO', 
					'SWEEP', 'SPAN', 'DIHEDRAL', 'TIP_CHORD', 'MOUNTING_ANGLE', 'WASHOUT', 'ROOT_CHORD', 'YOFFSET', 'CHORD',
					'ALPHA_L0', 'CL_ALPHA', 'CM_L0', 'CM_ALPHA', 'CD0', 'CD0_L', 'CD0_L2', 'CL_MAX']) :
		exit('Wrong parameter name ' + param + ' (at solve_all)')
		
	solve_results = []
	values_list = np.linspace(min, max, points)
	time_begin = time.time()
	for i in values_list :
		if param in ['AILERON', 'ELEVATOR', 'RUDDER', 'FLAP', 'V_MAG', 'ALPHA', 'BETA', 'RHO'] :
			solve_results.append(solve_once(param, i))
		if param in ['SWEEP', 'SPAN', 'DIHEDRAL', 'TIP_CHORD', 'MOUNTING_ANGLE', 'WASHOUT', 'ROOT_CHORD', 'YOFFSET', 'CHORD'] :
			update_geometry(param, i)
			solve_results.append(solve_once())
		if param in ['ALPHA_L0', 'CL_ALPHA', 'CM_L0', 'CM_ALPHA', 'CD0', 'CD0_L', 'CD0_L2', 'CL_MAX'] :
			update_airfoil(param, i)
			solve_results.append(solve_once())
			# print (solve_results[-1]['CL_ALPHA'])
		solve_results[-1]['value'] = i
		progress = round(len(solve_results)*100/points, 1)
		print('['+'#'*int(progress/10)+'-'*(10-int((progress/10)))+'] ' + format(int(progress), '02d') + '% in ' + str(round(time.time()-time_begin, 1)) + ' s', end = '\r')
	return solve_results

def units(data) :
	if data in ['AILERON', 'ELEVATOR', 'RUDDER', 'FLAP', 'ALPHA', 'BETA', 'SWEEP', 'DIHEDRAL', 'MOUNTING_ANGLE', 'WASHOUT', 'STALL_ANGLE'] :
		return ' [deg]'
	elif data in ['ALPHA_L0'] :
		return ' [rad]'
	elif data in ['CL_ALPHA', 'CM_ALPHA'] :
		return ' [1/rad]'
	else :
		return ''


def plot_data(data): # prints a plot of a list of data against another (['CL', 'alpha'] gives CL against alpha)
	i = 1
	for d in data:
		if not(d[0] in all_results[0]):
			exit('Unable to find data with the name "' + d[0] + '" in results')
		if not(d[1] in all_results[0]):
			exit('Unable to find data with the name "' + d[1] + '" in results')
			
		list_data_x = []
		list_data_y = []
		list_stalling_points_x = []
		list_stalling_points_y = []
		for j in range(len(all_results)):
			list_data_y.append(all_results[j][d[0]])
			list_data_x.append(all_results[j]['value'])
			if calc_stall_points :
				if all_results[j]['STALLING'] :
					list_stalling_points_x.append(all_results[j]['value'])
					list_stalling_points_y.append(all_results[j][d[0]])
		
		fig = plt.figure(i)
		i = i+1
		plt.plot(list_data_x, list_data_y)
		if calc_stall_points :
			plt.scatter(list_stalling_points_x, list_stalling_points_y, 30, 'r', 'X')
		stall_str = ''
		if d[1] == 'ALPHA' :
			control_state = {"aileron": aileron_def, "elevator": elevator_def, "rudder": rudder_def, "flap": 0}
			aero_state = {"V_mag": V_def, "alpha": alpha_def, "beta": beta_def, "rho": rho_def}
			stall = muAirplane.stall_onset(aero_state=aero_state, control_state=control_state)['alpha']
			if max(list_data_x) > stall :
				plt.plot([stall, stall], [min(list_data_y), max(list_data_y)], "r")
			stall_str = ' (Stalling at ' + str(round(stall, 2)) + ' deg)'
		plt.xlabel(d[1] + units(d[1]) + stall_str)
		plt.ylabel(d[0] + units(d[0]))
		plt.title(d[0] + ' against ' + d[1] + ', ' + str(len(list_data_x)) + ' points from ' + str(min(list_data_x)) + ' to ' + str(max(list_data_x)))
		plt.grid(True)
	plt.show()
	return 0

def study(param, points, data, stall_points = False): #Calculates and display results for chosen parameter
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
					'STALL_ANGLE', 'STALL_LIFT', 'STALL_SPEED' (Calculations get much longer)
	'''
	global calc_stall_angle
	global calc_stall_speed
	global calc_stall_points
	calc_stall_points = stall_points
	global all_results
	
	for p in param :
		p[0] = p[0].upper()
	for d in data :
		d = d.upper()
	
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
		print (' '*100, end = '\r') # Clear line
		print ('Study finished in ' + str(round(time.time()-time_start, 1)) + ' seconds')
		plot_data(plots_list)
	else :
		exit('Too many parameters')


study([['CL_alpha', 0, 10]], 100 , ['CL', 'CD'])

# ''' TESTING '''
# control_state = {"aileron": aileron_def, "elevator": elevator_def, "rudder": rudder_def, "flap": 0}
# aero_state = {"V_mag": V_def, "alpha": alpha_def, "beta": beta_def, "rho": rho_def}
# for k in range(10) :
	# control_state['flap'] = k
	# stalling = muAirplane.stall_onset(aero_state=aero_state, control_state=control_state)
	# print (str(stalling['alpha']) + ', ' + str(stalling['lift']))

remove(temp_filename) # Remove temporary file