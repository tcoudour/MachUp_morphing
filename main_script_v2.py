from __future__ import print_function
import machup.MU as MU
import numpy as np
import matplotlib.pyplot as plt
import json
from collections import OrderedDict
import time
from shutil import copy 
from os import remove, rename
from copy import deepcopy

filename = "SingleWingFlapTest.json" # input file
temp_filename = "temp_data.json" # copy of the input file that will be modified
copy(filename, temp_filename) # copy input file

default_control_state = { 
    "aileron": 0,
    "elevator": 0,
    "rudder": 0,
    "flap": 0
    }
default_aero_state = {
    "V_mag": 10,
    "alpha": 0,
    "beta": 0,
    "rho": 0.0023769
    }
weight = 100 # Newtons

# Model_states will contain every state of the wing/airplane
temp_airplane = MU.MachUp(temp_filename)
Model_states = [{ # Initial state
    'n' : 1,
    'airplane' : temp_airplane,
    'control_state' : deepcopy(default_control_state),
    'aero_state' : deepcopy(default_aero_state),
    'weight' : weight,
    'area' : temp_airplane.myairplane.get_long_ref()
             *temp_airplane.myairplane.get_lat_ref()
}]

def add_states(parameters_list , points) :
    '''
    This function adds states to the list of states Models_state
    Inputs :
        parameters_list is a list of dictionaries about the parameter(s) that
            will be changing across those states.
        The structure of these dictionaries is : {type, parameter, wing, final}
            type (string) : 'aero', 'control', 'geometry' or 'airfoil'
            parameter (string) : Name of the parameter, must fit the type
            wing (string) : Wing to modify for geometry/airfoil type parameters
                            Is not needed for aero or control parameters
            final (int or float) : The value the parameter will reach in the
                                   last state. Can be higher or lower than the
                                   current one.
        points (integer) is how much points (states) must be created.
    '''
    for p in parameters_list : # Check arguments
        if not p['type'] in ['aero', 'control', 'geometry', 'airfoil'] :
            exit('Wrong parameter type "' + p['type'] + '"')
        if p['type'] == 'aero' and not p['parameter'] in [
                'V_mag', 'alpha', 'beta', 'rho'] :
            exit('Wrong parameter name "' 
                 + p['parameter'] + '" for type "aero"')
        if p['type'] == 'control' and not p['parameter'] in [
                'aileron', 'elevator', 'rudder', 'flap'] :
            exit('Wrong parameter name "' 
                 + p['parameter'] + '" for type "control"')
        if p['type'] == 'geometry' and not p['parameter'] in [
                'sweep', 'span', 'dihedral', 'tip_chord', 'mounting_angle',
                'washout', 'root_chord', 'yoffset', 'chord'] :
            exit('Wrong parameter name "' 
                 + p['parameter'] + '" for type "geometry"')
        if p['type'] == 'airfoil' and not p['parameter'] in [
                'alpha_L0', 'CL_alpha', 'Cm_L0', 'Cm_alpha',
                'CD_0', 'CL_L', 'CD_L2', 'CL_max'] :
            exit('Wrong parameter name "'
                 + p['parameter'] + '" for type "airfoil"')
        if p['type'] in ['geometry', 'airfoil'] and p['wing'] is None :
            exit('Geometry/Airfoil parameters require a wing to be specified')
        if points <= 1 :
            exit('Wrong number of states')
            
    last_state = Model_states[-1]
    for i in range(points) : # For every point
        temp_state = {
            'n' : Model_states[-1]['n']+1,
            'control_state' : default_control_state,
            'aero_state' : deepcopy(default_aero_state),
            'weight' : weight
        }
        
        for p in parameters_list : # For every parameter
            if p['type'] == 'aero' :
                initial = last_state['aero_state'][p['parameter']]
                value_range = np.linspace(initial, p['final'], points+1)
                temp_state['aero_state'][p['parameter']] = value_range[i+1]
            elif p['type'] == 'control' :
                initial = last_state['control_state'][parameter]
                value_range = np.linspace(initial, p['final'], points+1)
                temp_state['control_state'][p['parameter']] = value_range[i+1]
            elif p['type'] == 'geometry' :
                if p['parameter'] == 'chord' :
                    initial = last_state['airplane'].myairplane._wings[p['wing']]._left_segment._dimensions['root_chord']
                else :
                    initial = last_state['airplane'].myairplane._wings[p['wing']]._left_segment._dimensions[p['parameter']]
                value_range = np.linspace(initial, p['final'], points+1)
                update_geometry(p['wing'], p['parameter'], value_range[i+1])
            elif p['type'] == 'airfoil' :
                initial = last_state['airplane'].myairplane._wings[p['wing']].airfoil(0)._properties[p['parameter']]
                value_range = np.linspace(initial, p['final'], points+1)
                update_airfoil(p['wing'], p['parameter'], value_range[i+1])
        
        temp_airplane = MU.MachUp(temp_filename)
        
        temp_state['airplane'] = temp_airplane
        temp_state['area'] = temp_airplane.myairplane.get_long_ref() * temp_airplane.myairplane.get_lat_ref()
        Model_states.append(temp_state)
    return 0

def update_geometry(wing, param, value) :
    '''
    This function modifies geometry parameters in the temporary .json file
    Inputs :
        wing (string) : Wing to be modified
        param (string) : Parameter to be modified
        value (int or float) : New value of the parameter
    '''
    if not (param in ['sweep', 'span', 'dihedral', 'tip_chord', 
            'mounting_angle', 'washout', 'root_chord', 'yoffset', 'chord']) :
        exit('Wrong parameter name "' + param + '" (at update_geometry)')
    with open(temp_filename, 'r+') as f :
        data = json.load(f, object_pairs_hook=OrderedDict)
        if param == 'chord' :
            data['wings'][wing]['root_chord'] = value
            data['wings'][wing]['tip_chord'] = value
        else :
            data['wings'][wing][param] = value
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()
    return 0

def update_airfoil(wing, param, value) : #Modifies the .json input file to change the airfoil
    '''
    This function modifies airfoil parameters in the temporary .json file
    Inputs :
        wing (string) : Wing to be modified
        param (string) : Parameter to be modified
        value (int or float) : New value of the parameter
    '''
    if not (param in ['alpha_L0', 'CL_alpha', 'Cm_L0', 'Cm_alpha', 'CD_0', 'CL_L', 'CD_L2', 'CL_max']) :
        exit('Wrong parameter name ' + param + ' (at update_airfoil)')
    with open(temp_filename, 'r+') as f :
        data = json.load(f, object_pairs_hook=OrderedDict)
        data['wings'][wing]['airfoils']['af1']['properties'][param] = value
        data['wings'][wing]['airfoils']['af2']['properties'][param] = value
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()
    return 0

def calculate(types) :
    '''
    This function runs calculations for all states contained in Model_states
    Input : type (list of strings)
        Contains one or several of 'aero', 'stall' and 'stall_speed'
        'aero' will run the basic calculations (Coefficients, Forces, Moments)
        'stall' will calculate stall angle and lift.
            /!\ Makes the calculation time longer
        'stall_speed' will calculate stall speed
            /!\ Makes the calculation time much longer
    '''
    print ('Starting calculations for', len(Model_states), 'states')
    time_begin = time.time()
    for s in Model_states :
        s['results'] = {}
        done = s['n']-1
        progress = round(done*100/len(Model_states), 1)
        print('['+'#'*int(progress/10)+'-'*(10-int((progress/10)))+'] ' + format(int(progress), '02d') + '% in ' + str(round(time.time()-time_begin, 1)) + ' s, now calculating state ' + str(s['n']), end = '\r')
        if 'aero' in types :
            state = deepcopy(s) # To protect the data in Model_states
            aero_results = state['airplane'].solve(aero_state = state['aero_state'], control_state = state['control_state'])
            s['results'] = aero_results
            s['results']['CL'] = (2*aero_results['FL'])/(state['aero_state']['rho']*(state['aero_state']['V_mag']**2)*state['area'])
            s['results']['CD'] = (2*aero_results['FD'])/(state['aero_state']['rho']*(state['aero_state']['V_mag']**2)*state['area'])
            s['results']['L/D'] = aero_results['CL'] / aero_results['CD']
        if 'stall' in types :
            state = deepcopy(s)
            stall_results = state['airplane'].stall_onset(aero_state=state['aero_state'], control_state=state['control_state'])
            s['results']['stall_angle'] = stall_results['alpha']
            s['results']['stall_lift'] = stall_results['lift']
        if 'stall_speed' in types :
            state = deepcopy(s)
            stall_speed_results = state['airplane'].stall_airspeed(weight=state['weight'], aero_state=state['aero_state'], control_state=state['control_state'])
            s['results']['stall_speed'] = stall_speed_results
        if 'stall_angle' in s['results'] :
            s['results']['stalling'] = s['aero_state']['alpha'] >= s['results']['stall_angle']
    print (' '*100, end = '\r') # Clear line
    print ('Calculations finished in ' + str(round(time.time()-time_begin, 1)) + ' seconds')

def plot_data(plot_list) : # [ [CL, CD, ALPHA], [] ]
    '''
    This function generates and display one or several plots from the results
    Input : plot_list (list of plots, each plot is a list)
            Each plot is a list containing at least two strings which are the
            names of the parameters.
            The last parameter will be on the x axis while all other will be
            on the y axis.
    Example : [['CL', 'CD', 'alpha'], ['stall_angle', 'alpha', 'n']]
        Will plot CL and CD against alpha on a first figure, and stall angle
        and alpha against state numbers on a second figure.
    '''
    figure_n = 1
    for p in plot_list : # For each plot
        if len(p) < 2 :
            exit('Not enough arguments to draw a plot')
        data_list = []
        for d in p : # For each data in the plot
            values_list = []
            for i in range(len(Model_states)) :
                if d in ['V_mag', 'alpha', 'beta', 'rho'] : # Aero
                    value = Model_states[i]['aero_state'][d]
                elif d in ['aileron', 'elevator', 'rudder', 'flap'] : # Control
                    value = Model_states[i]['control_state'][d]
                elif d in ['CL', 'CD', 'L/D', 'FL', 'FD', 'FS', 'FX', 'FY', 'FZ', 'MX', 'MY', 'MZ', 'stall_angle', 'stall_lift', 'stall_speed'] : # Results
                    value = Model_states[i]['results'][d]
                elif d in ['n', 'area'] : # Others
                    value = Model_states[i][d]
                elif type(d) is list : # Format ['data', 'wing']
                    if d[0] in ['sweep', 'span', 'dihedral', 'tip_chord', 'mounting_angle', 'washout', 'root_chord', 'yoffset', 'chord'] : # Geometry
                        if d[0] == 'chord' :
                            value = Model_states[i]['airplane'].myairplane._wings[d[1]]._left_segment._dimensions['root_chord']
                        else :
                            value = Model_states[i]['airplane'].myairplane._wings[d[1]]._left_segment._dimensions[d[0]]
                    elif d[0] in ['alpha_L0', 'CL_alpha', 'Cm_L0', 'Cm_alpha', 'CD_0', 'CL_L', 'CD_L2', 'CL_max'] : # Airfoil
                        value = Model_states[i]['airplane'].myairplane._wings[d[1]].get_wingsegments()[0].get_airfoils()[0]._properties[d[0]]
                else :
                    exit('Data not found')
                values_list.append(value)
            data_list.append(values_list)
            
        plt.figure(figure_n)
        figure_n += 1
        for i in range(len(data_list)-1) :
            plt.plot(data_list[-1], data_list[i])
        plt.grid(True)
        data_name_x = get_value_name(p[-1])
        data_name_y = ''
        for i in range(len(p)-1) :
            data_name_y += get_value_name(p[i])
            if i+1 in range(len(p)-1) :
                data_name_y += ', '
        plt.title(data_name_y + ' against ' + data_name_x + ', ' + str(len(Model_states)) + ' points')
        plt.xlabel(data_name_x + units(p[-1]))
        plt.ylabel(data_name_y)
        
        
    plt.show()

def get_value_name(value) :
    '''
    This function is used to get a value name for the plots.
    If value is a string, it returns the same string.
    If value is a list of 2 strings (for geometry and airfoil), it returns
    a combination of both (for example 'Wing_1/sweep')
    '''
    if type(value) is list :
        if len(value) == 2 :
            return value[1] + '/' + value[0]
        else :
            exit('Wrong list length when trying to get value name')
    else :
        return value

def units(data) :
    '''
    When given a data name, this functions returns its units if it knows them.
    (For use in plots or errors)
    '''
    if type(data) is list :
        data = data[0]
    if data in ['aileron', 'elevator', 'rudder', 'flap', 'alpha', 'beta', 'sweep', 'dihedral', 'mounting_angle', 'washout', 'stall_angle'] :
        return ' [deg]'
    elif data in ['alpha_L0'] :
        return ' [rad]'
    elif data in ['CL_alpha', 'Cm_alpha'] :
        return ' [1/rad]'
    else :
        return ''

if __name__ == "__main__":

    add_states([{'type':'aero', 'parameter':'alpha', 'wing':None, 'final':50}], points=19)
    # add_states([{'type':'geometry', 'parameter':'sweep', 'wing':'Wing_1', 'final':20}], points=19)
    # add_states([{'type':'geometry', 'parameter':'sweep', 'wing':'Wing_1', 'final':0}], points=20)
    # add_states([{'type':'airfoil', 'parameter':'CL_alpha', 'wing':'Wing_1', 'final':3}], points=3)

    # calculate(['aero', 'stall', 'stall_speed'])
    calculate(['aero'])

    # plot_data([['stall_angle', ['sweep', 'Wing_1'], 'n']])
    plot_data([['CL', 'CD', 'alpha']])

    # for s in Model_states :
        # print ('n :', s['n'])
        # print (s['aero_state'])
        # print (s['airplane'].myairplane._wings['Wing_1'].get_wingsegments()[0].get_airfoils()[0]._properties)
        # print (s['results'])

    remove(temp_filename) # Remove temporary file




