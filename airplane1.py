import machup.MU as MU
import numpy as np
import matplotlib.pyplot as plt


filename = "airplane1.json" #input file
muAirplane = MU.MachUp(filename)

long_ref = muAirplane.myairplane.get_long_ref()
lat_ref = muAirplane.myairplane.get_lat_ref()
area = long_ref * lat_ref

all_results = []



def solve_once(aileron=0, elevator=0, rudder=0, flap=0, Vmag=10, alpha=0, beta=0, rho=0.0023769):

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
							   # filename = 'results1.json'
							   ) # output file

	# Calculate Lift and Drag coefficients
	results['CL'] = (2*results['FL'])/(aero_state['rho']*(aero_state['V_mag']**2)*area)
	results['CD'] = (2*results['FD'])/(aero_state['rho']*(aero_state['V_mag']**2)*area)
		
	# Save parameters with results
	results['AILERON'] = control_state['aileron']
	results['ELEVATOR'] = control_state['elevator']
	results['RUDDER'] = control_state['rudder']
	results['FLAP'] = control_state['flap']
	
	results['VMAG'] = aero_state['V_mag']
	results['ALPHA'] = aero_state['alpha']
	results['BETA'] = aero_state['beta']
	results['RHO'] = aero_state['rho']
	
	all_results.append(results) # Contains FL, FD, FS, FX, FY, FZ, MX, MY, MZ; CL, CD; control parameters, aero parameters
	
	return 0;

def solve_all(data, min, max, points):
	
	values_list = np.linspace(min,max, points)
	for i in values_list :
		

	
def plot_data(*data): # prints a plot of a certain data against alpha
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
			list_data_x.append(all_results[j][d[1]])
		
		plt.figure(i)
		i = i+1
		plt.plot(list_data_x, list_data_y)
		plt.xlabel(d[1])
		plt.ylabel(d[0])
		plt.title(d[0] + ' against ' + d[1] + ', ' + str(alpha_values) + ' points')
		plt.grid(True)
	plt.show()
	return 0	




plot_data(['CL','alpha'], ['CD','alpha'])




