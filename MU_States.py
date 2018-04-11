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


class MU_States :

    def __init__(self, filename) :
        self.filename = filename
        self.temp_filename = "temp_data.json" # copy of the input
        copy(self.filename, self.temp_filename) # copy input file
        
        self.default_control_state = { 
            "aileron": 0,
            "elevator": 0,
            "rudder": 0,
            "flap": 0
            }
        self.default_aero_state = {
            "V_mag": 10,
            "alpha": 0,
            "beta": 0,
            "rho": 0.0023769
            }
        self.weight = 100 # Newtons
        
        self.states = []
        self.temp_airplane = MU.MachUp(self.temp_filename)
        self.states.append({ # Initial state
            'n' : 1,
            'airplane' : self.temp_airplane,
            'control_state' : deepcopy(self.default_control_state),
            'aero_state' : deepcopy(self.default_aero_state),
            'weight' : self.weight,
            'area' : self.temp_airplane.myairplane.get_long_ref()
                     *self.temp_airplane.myairplane.get_lat_ref()
            })

    def remove_temporary_file(self) :
        remove(self.temp_filename) # Remove temporary file
            
    def add_states(self, parameters_list , points) :
        '''
        This function adds states to the list of states Model_states
        Inputs :
            parameters_list is a list of dictionaries about the parameter(s) 
            that will be changing across those states.
            Their structure is : {type, parameter, wing, final}
                type (string) : 'aero', 'control', 'geometry' or 'airfoil'
                parameter (string) : Name of the parameter, must fit the type
                wing (string) : Wing to modify for geometry/airfoil type 
                                parameters, it's not needed for aero or control
                                parameters.
                final (int or float) : The value the parameter will reach in 
                                       the last state. Can be higher or lower 
                                       than the current one.
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
                exit(
                  'Geometry/Airfoil parameters require a wing to be specified')
            if points < 1 :
                exit('Wrong number of states')
                
        print ('Generating', points, 'states')
        time_begin = time.time()
                
        last_state = self.states[-1]
        for i in range(points) : # For every point
        
            progress = round(i*100/points, 1)
            print('['+'#'*int(progress/10)+'-'*(10-int((progress/10)))+'] ' 
                  + format(int(progress), '02d') + '% in ' 
                  + str(round(time.time()-time_begin, 1)) 
                  + ' s, now generating state ' + str(i), end = '\r')

            temp_state = deepcopy(last_state)
            temp_state['n'] = self.states[-1]['n']+1
            
            for p in parameters_list : # For every parameter
                if p['type'] == 'aero' :
                    initial = last_state['aero_state'][p['parameter']]
                    value_range = np.linspace(initial, p['final'], points+1)
                    temp_state['aero_state'][p['parameter']] = value_range[i+1]
                elif p['type'] == 'control' :
                    initial = last_state['control_state'][p['parameter']]
                    value_range = np.linspace(initial, p['final'], points+1)
                    temp_state['control_state'][
                        p['parameter']] = value_range[i+1]
                elif p['type'] == 'geometry' :
                    if p['parameter'] == 'chord' :
                        initial = last_state['airplane'].myairplane._wings[
                            p['wing']]._left_segment._dimensions['root_chord']
                    else :
                        initial = last_state['airplane'].myairplane._wings[
                            p['wing']]._left_segment._dimensions[
                            p['parameter']]
                    value_range = np.linspace(initial, p['final'], points+1)
                    update_geometry(
                        p['wing'], p['parameter'], value_range[i+1])
                elif p['type'] == 'airfoil' :
                    initial = last_state['airplane'].myairplane._wings[
                        p['wing']].airfoil(0)._properties[p['parameter']]
                    value_range = np.linspace(initial, p['final'], points+1)
                    update_airfoil(p['wing'], p['parameter'], value_range[i+1])
            
            temp_airplane = MU.MachUp(self.temp_filename)
            
            temp_state['airplane'] = temp_airplane
            temp_state['area'] = ( temp_airplane.myairplane.get_long_ref()
                               * temp_airplane.myairplane.get_lat_ref() )
            self.states.append(temp_state)
            
        print (' '*100, end = '\r') # Clear line
        print ('Generated ' + str(points) + ' states in ' 
               + str(round(time.time()-time_begin, 1)) + ' seconds')

    def add_states_double(self, parameters_list) :
        '''
        This function adds states for every value of two parameters.
        The input should be a list of 2 dictionaries containing these values :
            'type' (string) : the type of the parameter
            'param' (string) : the name of the parameter
            'wing' (string) (optional) : wing name, required for geometry
                and airfoil parameters.
            'final' : the final value the parameter must reach.
            'points' : how many points (states) must be created between the 
                current value and the final value
        For example, if you input :
            [{'type':'aero', 'parameter':'alpha', 'final':10, 'points':10}, 
            {'type':'aero', 'parameter':'beta', 'final':10, 'points':10}]
        you will get 100 states for alpha and beta.    
        '''
        if len(parameters_list) != 2 :
            exit('"add_states_double" expects two parameters dictionaries')
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
                exit(
                  'Geometry/Airfoil parameters require a wing to be specified')
            if p['points'] <= 1 :
                exit('Wrong number of states')
                
        print ('Generating', 
               str(parameters_list[0]['points']*parameters_list[1]['points']), 
               'states')
        time_begin = time.time()
                
        last_state = self.states[-1]
        for i in range(parameters_list[0]['points']) :
            row_state = deepcopy(last_state)
            if parameters_list[0]['type'] == 'aero' :
                initial = last_state[
                    'aero_state'][parameters_list[0]['parameter']]
                value_range = np.linspace(initial, 
                                parameters_list[0]['final'], 
                                parameters_list[0]['points'])
                row_state['aero_state'][parameters_list[0][
                    'parameter']] = value_range[i]
            elif parameters_list[0]['type'] == 'control' :
                initial = last_state[
                    'control_state'][parameters_list[0]['parameter']]
                value_range = np.linspace(initial, 
                                parameters_list[0]['final'], 
                                parameters_list[0]['points'])
                row_state['control_state'][parameters_list[0][
                    'parameter']] = value_range[i]
            elif parameters_list[0]['type'] == 'geometry' :
                if parameters_list[0]['parameter'] == 'chord' :
                    initial = last_state['airplane'].myairplane._wings[
                        parameters_list[0]['wing']]._left_segment._dimensions[
                        'root_chord']
                else :
                    initial = last_state['airplane'].myairplane._wings[
                        parameters_list[0]['wing']]._left_segment._dimensions[
                        parameters_list[0]['parameter']]
                value_range = np.linspace(initial, 
                                parameters_list[0]['final'], 
                                parameters_list[0]['points'])
                update_geometry(parameters_list[0]['wing'], 
                                parameters_list[0]['parameter'], 
                                value_range[i])
            elif parameters_list[0]['type'] == 'airfoil' :
                initial = last_state['airplane'].myairplane._wings[
                          p['wing']].airfoil(0)._properties[p['parameter']]
                value_range = np.linspace(initial, 
                                parameters_list[0]['final'], 
                                parameters_list[0]['points'])
                update_airfoil(parameters_list[0]['wing'], 
                               parameters_list[0]['parameter'], value_range[i])
                
            for j in range(parameters_list[1]['points']) :
            
                progress = round((i*parameters_list[1]['points'] + j)*100/(
                    parameters_list[0]['points']*parameters_list[1]['points']), 
                    1)
                print('['+'#'*int(progress/10)+'-'*(10-int((progress/10)))+'] ' 
                      + format(int(progress), '02d') + '% in ' 
                      + str(round(time.time()-time_begin, 1)) 
                      + ' s, now generating state ' + str(i*parameters_list[1][
                      'points'] + j), end = '\r')

                temp_state = deepcopy(row_state)
                temp_state['n'] = self.states[-1]['n']+1
                
                if parameters_list[1]['type'] == 'aero' :
                    initial = row_state[
                        'aero_state'][parameters_list[1]['parameter']]
                    value_range = np.linspace(initial, 
                                    parameters_list[1]['final'], 
                                    parameters_list[1]['points'])
                    temp_state['aero_state'][parameters_list[1][
                        'parameter']] = value_range[j]
                elif parameters_list[1]['type'] == 'control' :
                    initial = row_state['control_state'][parameters_list[1][
                        'parameter']]
                    value_range = np.linspace(initial, 
                                    parameters_list[1]['final'], 
                                    parameters_list[1]['points'])
                    temp_state['control_state'][parameters_list[1][
                        'parameter']] = value_range[j]
                elif parameters_list[1]['type'] == 'geometry' :
                    if parameters_list[1]['parameter'] == 'chord' :
                        initial = row_state['airplane'].myairplane._wings[
                            parameters_list[1][
                            'wing']]._left_segment._dimensions['root_chord']
                    else :
                        initial = row_state[
                            'airplane'].myairplane._wings[parameters_list[1][
                            'wing']]._left_segment._dimensions[
                            parameters_list[1]['parameter']]
                    value_range = np.linspace(initial, 
                                    parameters_list[1]['final'], 
                                    parameters_list[1]['points'])
                    update_geometry(parameters_list[1]['wing'], 
                                    parameters_list[1]['parameter'], 
                                    value_range[j])
                elif parameters_list[1]['type'] == 'airfoil' :
                    initial = row_state['airplane'].myairplane._wings[
                        parameters_list[1]['wing']].airfoil(0)._properties[
                        parameters_list[1]['parameter']]
                    value_range = np.linspace(initial, 
                                  parameters_list[1]['final'], 
                                  parameters_list[1]['points'])
                    update_airfoil(parameters_list[1]['wing'], 
                                   parameters_list[1]['parameter'], 
                                   value_range[j])
                
                temp_airplane = MU.MachUp(self.temp_filename)
                
                temp_state['airplane'] = temp_airplane
                temp_state['area'] = ( temp_airplane.myairplane.get_long_ref() 
                                     * temp_airplane.myairplane.get_lat_ref() )
                self.states.append(temp_state)
            
        print (' '*100, end = '\r') # Clear line
        print ('Generated ' 
               + str(parameters_list[0]['points']*parameters_list[1]['points']) 
               + ' states in ' + str(round(time.time()-time_begin, 1)) 
               + ' seconds')

    def update_geometry(self, wing, param, value) :
        '''
        This function modifies geometry parameters in the temporary .json file
        Inputs :
            wing (string) : Wing to be modified
            param (string) : Parameter to be modified
            value (int or float) : New value of the parameter
        '''
        if not (param in ['sweep', 'span', 'dihedral', 'tip_chord', 
                'mounting_angle', 'washout', 'root_chord', 
                'yoffset', 'chord']) :
            exit('Wrong parameter name "' + param + '" (at update_geometry)')
        with open(self.temp_filename, 'r+') as f :
            data = json.load(f, object_pairs_hook=OrderedDict)
            if param == 'chord' :
                data['wings'][wing]['root_chord'] = value
                data['wings'][wing]['tip_chord'] = value
            else :
                data['wings'][wing][param] = value
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

    def update_airfoil(self, wing, param, value) :
        '''
        This function modifies airfoil parameters in the temporary .json file
        Inputs :
            wing (string) : Wing to be modified
            param (string) : Parameter to be modified
            value (int or float) : New value of the parameter
        '''
        if not (param in ['alpha_L0', 'CL_alpha', 'Cm_L0', 'Cm_alpha', 
                          'CD_0', 'CL_L', 'CD_L2', 'CL_max']) :
            exit('Wrong parameter name ' + param + ' (at update_airfoil)')
        with open(self.temp_filename, 'r+') as f :
            data = json.load(f, object_pairs_hook=OrderedDict)
            data['wings'][wing]['airfoils']['af1']['properties'][param] = value
            data['wings'][wing]['airfoils']['af2']['properties'][param] = value
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

    def calculate(self, types) :
        '''
        This function runs calculations for all states contained in instance
        Input : type (list of strings)
            Contains one or several of 'aero', 'stall' and 'stall_speed'
            'aero' will run the basic calculations (Coeff., Forces, Moments)
            'stall' will calculate stall angle and lift.
                /!\ Makes the calculation time longer
            'stall_speed' will calculate stall speed
                /!\ Makes the calculation time much longer
        '''
        print ('Starting calculations for', len(self.states), 'states')
        time_begin = time.time()
        for s in self.states :
            s['results'] = {}
            done = s['n']-1
            progress = round(done*100/len(self.states), 1)
            print('['+'#'*int(progress/10)+'-'*(10-int((progress/10)))+'] ' 
                  + format(int(progress), '02d') + '% in ' 
                  + str(round(time.time()-time_begin, 1)) 
                  + ' s, now calculating state ' + str(s['n']), end = '\r')
            if 'aero' in types :
                state = deepcopy(s) # To protect the data in Model_states
                aero_results = state['airplane'].solve(
                                aero_state = state['aero_state'], 
                                control_state = state['control_state'])
                s['results'].update(aero_results)
                s['results']['CL'] = ((2*aero_results['FL'])
                                     /(state['aero_state']['rho']
                                        *(state['aero_state']['V_mag']**2)
                                        *state['area']))
                s['results']['CD'] = ((2*aero_results['FD'])
                                     /(state['aero_state']['rho']
                                        *(state['aero_state']['V_mag']**2)
                                        *state['area']))
                s['results']['L/D'] = s['results']['CL'] / s['results']['CD']
            if 'derivatives' in types :
                deriv_results_s = state[
                    'airplane'].stability_derivatives(aero_state = state[
                    'aero_state'], control_state = state['control_state'])
                s['results'].update(deriv_results_s)
                deriv_results_d = state[
                    'airplane'].damping_derivatives(aero_state = state[
                    'aero_state'], control_state = state['control_state'])
                s['results'].update(deriv_results_d)
                deriv_results_c = state[
                    'airplane'].control_derivatives(aero_state = state[
                    'aero_state'], control_state = state['control_state'])
                s['results'].update(deriv_results_c)
            if 'stall' in types :
                state = deepcopy(s)
                stall_results = state['airplane'].stall_onset(
                    aero_state=state['aero_state'],
                    control_state=state['control_state'])
                s['results']['stall_angle'] = stall_results['alpha']
                s['results']['stall_lift'] = stall_results['lift']
            if 'stall_speed' in types :
                state = deepcopy(s)
                stall_speed_results = state['airplane'].stall_airspeed(
                    weight=state['weight'],
                    aero_state=state['aero_state'],
                    control_state=state['control_state'])
                s['results']['stall_speed'] = stall_speed_results
            if 'stall_angle' in s['results'] :
                s['results']['stalling'] = ( s['aero_state']['alpha'] 
                                          >= s['results']['stall_angle'] )
        print (' '*100, end = '\r') # Clear line
        print ('Calculations finished in ', 
               round(time.time()-time_begin, 1), 
               ' seconds')

    def plot_data(self, plot_list) :
        '''
        Generates and display one or several plots from the results
        Input : plot_list (list of plots, each plot is a list)
                Each plot is a list containing at least two strings which are 
                the names of the parameters.
                The last parameter will be on the x axis while all other will 
                be on the y axis.
        Example : [['CL', 'CD', 'alpha'], ['stall_angle', 'alpha', 'n']]
            Will plot CL and CD against alpha on a first figure, and stall 
            angle and alpha against state numbers on a second figure.
            If a parameter requires a wing, it must be a list containing the
            name of the parameter first and the name of the wing.
            Example : [['CL', 'stall_angle', ['sweep', 'Wing_1']]]
        '''
        figure_n = 1
        for p in plot_list : # For each plot
            if len(p) < 2 :
                exit('Not enough arguments to draw a plot')
            data_list = []
            for d in p : # For each data in the plot
                values_list = []
                for i in range(len(self.states)) :
                    value = self.get_parameter(self.states[i], d)
                    values_list.append(value)
                data_list.append(values_list)
                
            plt.figure(figure_n)
            figure_n += 1
            for i in range(len(data_list)-1) :
                plt.plot(data_list[-1], data_list[i])
            plt.grid(True)
            data_name_x = self.get_value_name(p[-1])
            data_name_y = ''
            legend = []
            for i in range(len(p)-1) :
                data_name_y += self.get_value_name(p[i])
                if i+1 in range(len(p)-1) :
                    data_name_y += ', '
                legend.append(self.get_value_name(p[i]))
            plt.title(data_name_y + ' against ' + data_name_x + ', ' 
                      + str(len(self.states)) + ' points')
            plt.xlabel(data_name_x + self.units(p[-1]))
            plt.ylabel(data_name_y)
            plt.legend(legend)
            
        plt.show()

    def plot_2D(self, data) :
        '''
        Generates a 2D color plot.
        data is a list of 3 string/lists of data names for x axis, y axis then 
        color (z axis ?)
        Example : "plot_2D(['alpha', 'beta', 'CL'])" will generate a plot of
        CL (color) against alpha (x) and beta (y)
        '''
        if len(data) != 3 :
            exit ('2D plot needs 3 parameters')
            
        list_x = []
        list_y = []
        list_c = []
        lists = [list_x, list_y, list_c]
        for d in range(3) :
            for i in range(len(self.states)) :
                value = self.get_parameter(self.states[i], data[d])
                lists[d].append(value)
            
        plt.scatter(list_x, list_y, c=list_c, cmap='inferno', marker='.')
        plt.colorbar()
        
        data_name_x = self.get_value_name(data[0])
        data_name_y = self.get_value_name(data[1])
        data_name_c = self.get_value_name(data[2])
        plt.title(data_name_c + ' against ' + data_name_x + ' and ' 
                  + data_name_y + ', ' + str(len(self.states)) + ' points')
        plt.xlabel(data_name_x + self.units(data[0]))
        plt.ylabel(data_name_y + self.units(data[1]))
        
        plt.show()  
        
    def get_value_name(self, value) :
        '''
        This function is used to get a value name for the plots.
        If value is a string, it returns the same string.
        If value is a list of 2 strings (for geometry and airfoil), it returns
        a combination of both (for example 'Wing_1/sweep')
        '''
        if type(value) is list :
            if len(value) == 2 :
                return value[1] + '.' + value[0]
            else :
                exit('Wrong list length when trying to get value name')
        else :
            return value

    def units(self, data) :
        '''
        When given a data name, this functions returns its units if it known.
        (For use in plots or errors)
        '''
        if type(data) is list :
            data = data[0]
        if data in ['aileron', 'elevator', 'rudder', 'flap', 'alpha', 'beta', 
                    'sweep', 'dihedral', 'mounting_angle', 'washout', 
                    'stall_angle'] :
            return ' [deg]'
        elif data in ['alpha_L0'] :
            return ' [rad]'
        elif data in ['CL_alpha', 'Cm_alpha'] :
            return ' [1/rad]'
        else :
            return ''

    def get_parameter(self, state, param) :
        '''
        Returns a parameter from a state
        param is either a string (for parameters not requiring a wing) or a 
        list containing the name of the parameter, then the name of the wing 
        (for geometry and airfoil parameters).
        '''
        if param in ['V_mag', 'alpha', 'beta', 'rho'] : # Aero
            return state['aero_state'][param]
        elif param in ['aileron', 'elevator', 'rudder', 'flap'] : # Control
            return state['control_state'][param]
        elif param in ['CL', 'CD', 'L/D', 'FL', 'FD', 'FS', 
                       'FX', 'FY', 'FZ', 'MX', 'MY', 'MZ', 
                       'stall_angle', 'stall_lift', 'stall_speed',
                       'CL_a', 'CD_a', 'CS_a', 'CX_a', 'CY_a', 'CZ_a', 
                       'Cl_a', 'Cm_a', 'Cn_a', 'CL_b', 'CD_b', 'CS_b', 
                       'CX_b', 'CY_b', 'CZ_b', 'Cl_b', 'Cm_b', 'Cn_b', 
                       'CL_pbar', 'CD_pbar', 'CS_pbar', 
                       'CX_pbar', 'CY_pbar', 'CZ_pbar', 
                       'Cl_pbar', 'Cm_pbar', 'Cn_pbar', 
                       'CL_qbar', 'CD_qbar', 'CS_qbar', 
                       'CX_qbar', 'CY_qbar', 'CZ_qbar', 
                       'Cl_qbar', 'Cm_qbar', 'Cn_qbar', 
                       'CL_rbar', 'CD_rbar', 'CS_rbar', 
                       'CX_rbar', 'CY_rbar', 'CZ_rbar', 
                       'Cl_rbar', 'Cm_rbar', 'Cn_rbar', 
                       'CL_da', 'CD_da', 'CS_da', 'CX_da', 'CY_da', 'CZ_da', 
                       'Cl_da', 'Cm_da', 'Cn_da', 'CL_de', 'CD_de', 'CS_de', 
                       'CX_de', 'CY_de', 'CZ_de', 'Cl_de', 'Cm_de', 'Cn_de', 
                       'CL_dr', 'CD_dr', 'CS_dr', 'CX_dr', 'CY_dr', 'CZ_dr', 
                       'Cl_dr', 'Cm_dr', 'Cn_dr', 'CL_df', 'CD_df', 'CS_df', 
                       'CX_df', 'CY_df', 'CZ_df', 'Cl_df', 'Cm_df', 'Cn_df', 
                       'stalling'] : # Results
            return state['results'][param]
        elif param in ['n', 'area'] : # Others
            return state[param]
        elif type(param) is list : # Format ['data', 'wing']
            if param[0] in ['sweep', 'span', 'dihedral', 'tip_chord', 
                            'mounting_angle', 'washout', 'root_chord', 
                            'yoffset', 'chord'] : # Geometry
                if param[0] == 'chord' :
                    return state['airplane'].myairplane._wings[
                        param[1]]._left_segment._dimensions['root_chord']
                else :
                    return state['airplane'].myairplane._wings[
                        param[1]]._left_segment._dimensions[param[0]]
            elif param[0] in ['alpha_L0', 'CL_alpha', 'Cm_L0', 'Cm_alpha', 
                          'CD_0', 'CL_L', 'CD_L2', 'CL_max'] : # Airfoil
                return state['airplane'].myairplane._wings[
                    param[1]].get_wingsegments()[0].get_airfoils()[
                    0]._properties[param[0]]
        else :
            exit('Data not found')

            
# add_states([{'type':'aero', 'parameter':'alpha', 'final':20}], points=99)
# add_states([{'type':'control', 'parameter':'flap', 'final':50}], points=99)
# add_states([{'type':'geometry', 'parameter':'sweep', 'wing':'Wing_1', 'final':20}], points=19)
# add_states([{'type':'geometry', 'parameter':'sweep', 'wing':'Wing_1', 'final':0}], points=20)
# add_states([{'type':'airfoil', 'parameter':'CL_alpha', 'wing':'Wing_1', 'final':24}], points=99)

# add_states([{'type':'geometry', 'parameter':'dihedral', 'wing':'Wing_1', 'final':-20}], points=100)

# add_states([{'type':'geometry', 'parameter':'dihedral', 'wing':'Wing_1', 'final':-20},
            # {'type':'geometry', 'parameter':'washout', 'wing':'Wing_1', 'final':-20}
            # ], points=1)

# add_states_double([
    # {'type':'aero', 'parameter':'alpha', 'final':10, 'points':11}, 
    # {'type':'aero', 'parameter':'beta', 'final':10, 'points':11}])
# add_states_double([
    # {'type':'geometry', 'parameter':'dihedral', 'wing':'Wing_1', 'final':20, 'points':50}, 
    # {'type':'geometry', 'parameter':'washout', 'wing':'Wing_1', 'final':20, 'points':50}
    # ])

# calculate(['aero'])
# calculate(['aero', 'derivatives', 'stall'])
# calculate(['aero', 'stall', 'stall_speed'])

# plot_data([['CL', 'CL_df', 'flap']])
# plot_data([['stall_angle', 'n']])
# plot_data([['CL', 'CD', ['CL_alpha', 'Wing_1']],['alpha', 'stall_angle', ['CL_alpha', 'Wing_1']]])
# plot_data([['stall_angle', ['dihedral', 'Wing_1']]])

# plot_2D(['alpha', 'beta', 'CL'])
# plot_2D([['washout', 'Wing_1'], ['dihedral', 'Wing_1'], 'stalling'])
