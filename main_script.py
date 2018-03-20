import machup.MU as MU
import numpy as np
import matplotlib.pyplot as plt
import json
from collections import OrderedDict

filename = "SingleWing.json" #input file
with open(filename, 'r+') as f : #Save the original data from the file
	backup_data = json.load(f, object_pairs_hook=OrderedDict)

muAirplane = MU.MachUp(filename)

long_ref = muAirplane.myairplane.get_long_ref()
lat_ref = muAirplane.myairplane.get_lat_ref()
area = long_ref * lat_ref

all_results = []

#Default parameters
aileron_def = 0
elevator_def = 0
rudder_def = 0
flap_def = 0
V_def = 10
alpha_def = 0
beta_def = 0
rho_def = 0.0023769

def solve_once(aileron=aileron_def, elevator=elevator_def, rudder=rudder_def, flap=flap_def, Vmag=V_def, alpha=alpha_def, beta=beta_def, rho=rho_def):

	control_state = {
		"aileron": aileron,
		"elevator": elevator,
		"rudder": rudder,
		"flap": flap,
	}
	aero_state = {
		"V_mag": Vmag,
		"alpha": alpha,
		"beta": beta,
		"rho": rho
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
	
	results['VMAG'] = aero_state['V_mag']
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
	
	# Save airfoil data
	results['ALPHA_L0'] = muAirplane.myairplane._wings['Wing_1'].airfoil(0)._properties['alpha_L0']
	results['CL_ALPHA'] = muAirplane.myairplane._wings['Wing_1'].airfoil(0)._properties['CL_alpha']
	results['CM_L0'] = muAirplane.myairplane._wings['Wing_1'].airfoil(0)._properties['Cm_L0']
	results['CM_ALPHA'] = muAirplane.myairplane._wings['Wing_1'].airfoil(0)._properties['Cm_alpha']
	results['CD0'] = muAirplane.myairplane._wings['Wing_1'].airfoil(0)._properties['CD_0']
	results['CD0_L'] = muAirplane.myairplane._wings['Wing_1'].airfoil(0)._properties['CD_L']
	results['CD0_L2'] = muAirplane.myairplane._wings['Wing_1'].airfoil(0)._properties['CD_L2']
	results['CL_MAX'] = muAirplane.myairplane._wings['Wing_1'].airfoil(0)._properties['CL_max']
	
	all_results.append(results) # Contains FL, FD, FS, FX, FY, FZ, MX, MY, MZ; CL, CD, L/D; control parameters, aero parameters, wing geometry, airfoil
	
	return 0;

def update_geometry(param, value) : #Modifies the .json input file to change the geometry
	global muAirplane
	if not (param in ['sweep', 'span', 'dihedral', 'tip_chord', 'mounting_angle', 'washout', 'root_chord', 'yoffset']) :
		print 'Wrong parameter name'
		return 1
	with open(filename, 'r+') as f :
		data = json.load(f, object_pairs_hook=OrderedDict)
		data['wings']['Wing_1'][param] = value
		f.seek(0)
		json.dump(data, f, indent=4)
		f.truncate()
	muAirplane = MU.MachUp(filename)
	return 0

def update_airfoil(param, value) : #Modifies the .json input file to change the airfoil
	global muAirplane
	if not (param in ['alpha_L0', 'CL_alpha', 'Cm_L0', 'Cm_alpha', 'CD0', 'CD0_L', 'CD0_L2', 'CL_max']) :
		print 'Wrong parameter name'
		return 1
	with open(filename, 'r+') as f :
		data = json.load(f, object_pairs_hook=OrderedDict)
		data['wings']['Wing_1']['airfoils']['af1']['properties'][param] = value
		data['wings']['Wing_1']['airfoils']['af2']['properties'][param] = value
		f.seek(0)
		json.dump(data, f, indent=4)
		f.truncate()
	muAirplane = MU.MachUp(filename)
	return 0


def solve_all(param, min, max, points):
	global all_results
	
	if not (param in ['aileron', 'elevator', 'rudder', 'flap', 'Vmag', 'alpha', 'beta', 'rho', 
					'sweep', 'span', 'dihedral', 'tip_chord', 'mounting_angle', 'washout', 'root_chord', 'yoffset',
					'alpha_L0', 'CL_alpha', 'Cm_L0', 'Cm_alpha', 'CD0', 'CD0_L', 'CD0_L2', 'CL_max']) :
		print 'Wrong parameter name'
		return 1
		
	all_results = []
	values_list = np.linspace(min, max, points)
	for i in values_list :
		if param == 'aileron' :
			solve_once(aileron = i)
		if param == 'elevator' :
			solve_once(elevator = i)
		if param == 'rudder' :
			solve_once(rudder = i)
		if param == 'flap' :
			solve_once(flap = i)
		if param == 'Vmag' :
			solve_once(Vmag = i)
		if param == 'alpha' :
			solve_once(alpha = i)
		if param == 'beta' :
			solve_once(beta = i)
		if param == 'rho' :
			solve_once(rho = i)
		if param in ['sweep', 'span', 'dihedral', 'tip_chord', 'mounting_angle', 'washout', 'root_chord', 'yoffset'] :
			update_geometry(param, i)
			solve_once()
		if param in ['alpha_L0', 'CL_alpha', 'Cm_L0', 'Cm_alpha', 'CD0', 'CD0_L', 'CD0_L2', 'CL_max'] :
			update_airfoil(param, i)
			solve_once()
		all_results[len(all_results)-1]['value'] = i
	return 0

def plot_data(data): # prints a plot of a list of data against another (['CL', 'alpha'] gives CL against alpha)
	i = 1
	for d in data:
		d[0] = d[0].upper() #uppercase
		d[1] = d[1].upper()
		if not(d[0] in all_results[0]):
			print 'Unable to find data with the name "' + d[0] + '" in results'
			return 1
		if not(d[1] in all_results[0]):
			print 'Unable to find data with the name "' + d[1] + '" in results'
			return 1
			
		list_data_x = []
		list_data_y = []
		for j in range(len(all_results)):
			list_data_y.append(all_results[j][d[0]])
			# list_data_x.append(all_results[j][d[1]])
			list_data_x.append(all_results[j]['value'])
		
		plt.figure(i)
		i = i+1
		plt.plot(list_data_x, list_data_y)
		plt.xlabel(d[1])
		plt.ylabel(d[0])
		plt.title(d[0] + ' against ' + d[1] + ', ' + str(len(list_data_x)) + ' points')
		plt.grid(True)
	plt.show()
	return 0

def study(param, min, max, points, data): #Calculates and display results for chosen parameter
	#Parameter can be 'aileron', 'elevator', 'rudder', 'flap', 'Vmag', 'alpha', 'beta', 'rho',
	#					'sweep', 'span', 'dihedral', 'tip_chord', 'mounting_angle', 'washout', 'root_chord', 'yoffset',
	#					'alpha_L0', 'CL_alpha', 'Cm_L0', 'Cm_alpha', 'CD0', 'CD0_L', 'CD0_L2', 'CL_max'
	#Data can be 'CL', 'CD', 'L/D', 'FL', 'FD', 'FS', 'FX', 'FY', 'FZ', 'MX', 'MY', 'MZ'
	#You can input multiple data
	solve_all(param, min, max, points)
	plots_list = []
	for d in data :
		plots_list.append([d, param])
	plot_data(plots_list)


study('alpha', 1, 20, 20, ['CL', 'CD', 'L/D'])


with open(filename, 'r+') as f : #Restore file to its original state
	f.seek(0)
	json.dump(backup_data, f, indent=4)
	f.truncate()
