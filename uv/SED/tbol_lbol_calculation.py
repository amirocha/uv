'''
***************************************************************************************
 Program for calculating Tbol and Lbol with 2 methods:
 1) Trapezodial sumation of all the data collected
 2) Linear interpolation and trapezodial sumation of these new
 generated data. For the interpolation we use the program: "loglev.pro"

 The program generates the SEDs plots (saved in the folder: "plots")

 Modification;10-May-2011
***************************************************************************************
'''
# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import math as m
import numpy as np
from scipy.interpolate import interp1d
from scipy.interpolate import splrep
from scipy.interpolate import splev
import scipy.integrate as integrate


from matplotlib import rc
rc('font',**{'family':'serif','serif':['Helvetica']})


  
def read_data(filename):
	file1 = open(filename,'r')
	data = file1.readlines()
	file1.close()

	return data

def sort_points(list_to_sort, other_list):
	if len(list_to_sort) != len(other_list):
		raise 
	merged_list = [(list_to_sort[i], other_list[i]) for i in range(len(list_to_sort))]
	sorted_list = sorted(merged_list, key=lambda x: x[0])
	return [elem[0] for elem in sorted_list], [elem[1] for elem in sorted_list]


def read_columns(data):
	wave_lenghts = []
	fluxes =[]

	for i in range(len(data)): 
		line=data[i]
		wave_lenghts.append(float(line.split()[0]))
		fluxes.append(float(line.split()[1]))

	return wave_lenghts, fluxes
  
def wavelenght2freq(wavelenght_list):  #or freq2wavelenght
	freq_list = [(c/wave) for wave in wavelenght_list]
	return freq_list

def list_in_log_scale(input_list):
	output_list = [m.log10(elem) for elem in input_list]
	return output_list

def interpolate(freq, fluxes, interpolation_type='cubic', factor=1.):
	
	interpolation = interp1d(freq, fluxes, kind=interpolation_type, fill_value="extrapolate")
	freq_interpol = np.arange(freq[-1],freq[0],(freq[0]+freq[-1])/(factor*len(freq)))
	fluxes_interpol = interpolation(freq_interpol)
	return interpolation, freq_interpol, fluxes_interpol  #function, x_axis, y_axis

def interpolate_new(freq, fluxes, interpolation_type=3, factor=100.):

	freq_sorted, fluxes_sorted = sort_points(freq, fluxes)
	freq_interpol = np.arange(freq[-1],freq[0],(freq[0]+freq[-1])/(factor*len(freq)))
	interpolation = splrep(freq_sorted, fluxes_sorted, k=3, task=0, s=0, t=None)
	fluxes_interpol = splev(freq_interpol, interpolation)
	return freq_interpol, fluxes_interpol  #function, x_axis, y_axis

def integrate_function(function, start, end, steps=10000):
	sum_=0.
	dx=(end-start)/steps
	while start < end:
		sum_ += function(start)*dx
		start += dx
	return sum_
		 
def integrate(x, y):
	sum_=0.
	for i in range(1,len(x)):
		sum_ += ((y[i]+y[i-1])/2.)*(abs(x[i]-x[i-1]))
	return sum_

def calculate_flux_nu(flux_list, freq_list):
	if len(flux_list) != len(freq_list):
		raise 
	new_list = [flux_list[i]*freq_list[i] for i in range(len(freq_list))]
	return new_list

def log_list_in_linear_scale(log_list):
	new_list = [10**(elem) for elem in log_list]
	return new_list

def flux_in_watts(flux_list):
	flux_watts = [1e-26*flux for flux in flux_list]
	return flux_watts

def calculate_tbol_lbol(freq_list, flux_list, integral):
	#print(flux_list)
	tbol = (1.25e-11*integrate(freq_list,flux_list))/integral
	lbol = (integral*4.0*m.pi*(dist*3.0857e16)**2)/L_sun

	return tbol, lbol


file_name='smm8.inp'   
  
  
dist=436. #Ortiz-Leon 2017

c=2.9979e14 #in microns
L_sun = 3.86e26 #W  
 
#-------------------------------------------------------


minii=1.0                     #for the interpolation, keep it always 1
mini=1.0



#-------------------------------------------------------


file1=read_data(file_name)   #wczytuje plik smm [dl. fali [mikrony] i flux [Jy]

  
wavelenghts = read_columns(file1)[0]
fluxes = read_columns(file1)[1]
freq = wavelenght2freq(wavelenghts)
 

#------interpolation-----------------------------------


#----------------------fluxes in Watts

fluxes_watts=flux_in_watts(fluxes)

#-----------------------logaritmic scale

freq_log=list_in_log_scale(freq)
fluxes_log=list_in_log_scale(fluxes_watts)


#####________new_method__________########

freq_interpol, flux_interpol = interpolate_new(freq, fluxes_watts)

freq_interpol_log, flux_interpol_log = interpolate_new(freq_log, fluxes_log)

flux_interpol = log_list_in_linear_scale(flux_interpol_log)
freq_interpol = log_list_in_linear_scale(freq_interpol_log)

integral = integrate(freq_interpol, flux_interpol)
fluxfreq_interpol=calculate_flux_nu(flux_interpol, freq_interpol)   
tbol_interpol, lbol_interpol=calculate_tbol_lbol(freq_interpol,fluxfreq_interpol,integral)

print(lbol_interpol, tbol_interpol)

#####________L/T sbmm__________########
wavelenght_interpol=wavelenght2freq(freq_interpol)
sbmm_wavelenghts=[]
sbmm_fluxes=[]
for i in range(len(wavelenght_interpol)):
	if wavelenght_interpol[i] > 350: #Enoch2009
		sbmm_wavelenghts.append(wavelenght_interpol[i])
		sbmm_fluxes.append(wavelenght_interpol[i])
sbmm_freq=wavelenght2freq(sbmm_wavelenghts)
sbmm_integral = integrate(sbmm_freq, sbmm_fluxes)
sbmm_fluxfreq=calculate_flux_nu(sbmm_fluxes, sbmm_freq)   
sbmm_tbol, sbmm_lbol = calculate_tbol_lbol(sbmm_freq,sbmm_fluxfreq,sbmm_integral)

print(sbmm_tbol, sbmm_lbol)


#####________old_method__________########
'''
l='linear'
c='cubic'
q='quadratic'

interpolation, freq_interpol, flux_interpol = interpolate(freq, fluxes_watts, l, factor=100)

interpolation_log, freq_interpol_log, flux_interpol_log = interpolate(freq_log, fluxes_log, l, factor=100)

#interpolation_allpoints, freq_allpoints_interpol, flux_allpoints_interpol = interpolate(all_points_freq, all_points_fluxes_watts, l, 100.)

#interpolation_allpoints_log, freq_allpoints_interpol_log, flux_allpoints_interpol_log = interpolate(all_points_freq_log, all_points_fluxes_log, l, 100.)


#trapez_integral=integrate(freq, fluxes_watts)
#trapez_integral_all=integrate(all_points_freq, all_points_fluxes_watts)
integral_interpol=integrate_function(interpolation, freq_interpol[0], freq_interpol[-1])  #value
#allpoints_integral=integrate_function(interpolation_allpoints,  freq_allpoints_interpol[0],  freq_allpoints_interpol[-1]) #value

fluxfreq_interpol=calculate_flux_nu(flux_interpol, freq_interpol)   #list
#fluxfreq_interpol_allpoints=calculate_flux_nu(flux_allpoints_interpol, freq_allpoints_interpol) #list
fluxfreq_watts=calculate_flux_nu(fluxes_watts, freq)
#fluxfreq_watts_all=calculate_flux_nu(all_points_fluxes_watts, all_points_freq)


#tbol_trapez, lbol_trapez=calculate_tbol_lbol(freq,fluxfreq_watts,trapez_integral)
#tbol_trapez_all, lbol_trapez_all=calculate_tbol_lbol(all_points_freq,fluxfreq_watts_all,trapez_integral_all)
tbol_interpol, lbol_interpol=calculate_tbol_lbol(freq_interpol,fluxfreq_interpol,integral_interpol)
#tbol_interpol_all, lbol_interpol_all=calculate_tbol_lbol(freq_allpoints_interpol,fluxfreq_interpol_allpoints,allpoints_integral)

print(lbol_interpol, tbol_interpol)



#newpoints_freq_log = [m.log10(freq) for freq in newpoints_freq]
#newpoints_flux_div_freq_log = [m.log10(1e-26*newpoints_fluxes[i]*newpoints_freq[i]) for i in range(len(newpoints_fluxes))] 
fluxfreq_watts_log = list_in_log_scale(fluxfreq_watts)
#fluxfreq_watts_allpoints_log = list_in_log_scale(fluxfreq_watts_all)
'''

#writting to file
file2=open('sed_smm8.txt','w')
for i in range(len(freq_log)): 
	file2.write("%f %f \n" % (freq_log[i], fluxes_log[i]))
file2.close()



fig, ax = plt.subplots()
plt.title('SMM8')
#plt.ylabel(r'log(F$\cdot \nu$) [W $\cdot$ m$^{-2}$]')
plt.ylabel(r'log(F) [W $\cdot$ m$^{-2}$ $\cdot$ Hz$^{-1}$]')
plt.xlabel(r'log($\nu$) [Hz]')
plt.plot(freq_log, fluxes_log, 'ro', linewidth=1)
#plt.plot(freq, fluxes_watts, 'ro', linewidth=1)
plt.plot(freq_interpol_log, flux_interpol_log, 'k-', linewidth=0.6)
#plt.plot(freq_interpol, flux_interpol, 'k-', linewidth=0.6)
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
ax.text(0.05, 0.15, r'T$_{bol}$ = '+"%.2f" % round(tbol_interpol,2)+' K', transform=ax.transAxes, fontsize=12, verticalalignment='bottom', bbox=props)
ax.text(0.05, 0.05, r'L$_{bol}$ = '+"%.2f" % round(lbol_interpol,2)+r' L$_{Sun}$', transform=ax.transAxes, fontsize=12, verticalalignment='bottom', bbox=props)
#plt.plot(newpoints_freq_log, newpoints_flux_div_freq_log, 'bo', linewidth=1)

plt.savefig('SED_SMM8_cubic_interpolation_photo.png')
plt.close()

'''
#------calculate Lsubmm-----------------------------------

w_sbmm_interpol=loglev(minl=350,maxl=3.0e3,nlev=200)
s_sbmm_interpol=10.0^interpol(m.log10(w2), m.log10(s2), kind='cubic')
  
num=len(w)
integral=np.trapz(w_sbmm_interpol,s_sbmm_interpol)

lum_submm_interpol=(integral*4.0*m.pi*(dist*3.0857e16)**2)/3.86e26

  
lum_submm_vel_lum_interpol=100*lumsub_interpol/lum_interpol
  

print(lum_interpol, lum_submm_vel_lum_interpol)


'''

