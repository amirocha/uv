"""Flux correlation"""
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stat
import math as m

DIST=436. #Ortiz-Leon 2017
L_sun = 3.86e26 #W  
freq = {'CN': 113490985000}
 

def read_data(filename):
	file = open(filename,'r')
	data = file.readlines()
	file.close()

	return data

def write_data(end_filename, data, slope, intercept, pearson, stderr):
	file = open(end_filename,'w')
	for SMM, CN, HCN in data:
		file.write(f'{SMM:10.5} {CN:10.5} {HCN:10.5}\n')
	file.write(f'\n slope:{slope:10.5} intercept:{intercept:10.5} stderr:{stderr:10.5} pearson:{pearson:10.5}\n')
	file.close()

def create_flux_file(data):
	fluxes = []
	for i in range(1,len(data)):
		line = data[i].split()
		previous_line = data[i-1].split()
		if line[1] == 'hcn10' and previous_line[1] == 'cn10':
			fluxes.append((line[0], float(previous_line[2]), float(line[2]), float(data[i+1].split()[2]))) # source CNflux, HCNflux, CSflux
	return fluxes

def plot_correlation(x, y, a, b, pearson):
	Y = [elem*a+b for elem in x]

	fig = plt.figure(1)
	ax = fig.add_subplot(111)
	
	ax.set_ylabel("I(CN 1-0) [K km/s]")
	ax.set_xlabel(r"L$_{\mathrm{bol}}$ [L$_\odot$]")

	major_ticks_x = np.arange(0, 85, 5)
	major_ticks_y = np.arange(0, 30, 2)

	ax.set_xticks(major_ticks_x)
	ax.set_yticks(major_ticks_y)

	sources_list=['SMM8','SMM5','SMM2','SMM4','SMM12','SMM10','SMM3','SMM9','SMM6','SMM1']  #Lbol increasing
	for i in range(len(sources_list)):
		if i ==4:
			ax.text(x[i]-9.2, y[i], 'SMM12')
		elif i == 0:
			ax.text(x[i]-4.2, y[i], 'SMM8')
		else:
			ax.text(x[i]+0.2, y[i], sources_list[i])

	props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)	
	ax.text(0.45, 0.05, 'Pearson coefficient = '+str(round(pearson)) , transform=ax.transAxes, fontsize=14,
        verticalalignment='bottom', bbox=props)
	
	plt.plot(x, y, 'r.', ms=4.9)
	plt.plot(x, Y, 'k-', linewidth=0.5)

	plt.savefig('CN_Lbol_correlation_log', format='eps')
	plt.close()

def calculate_pearson(x, y):
	pearson = stat.pearsonr(x, y)
	print(pearson)

	return pearson[0]

def fit_linear_regression(x, y):
	slope, intercept, r_value, p_value, stderr = stat.linregress(x,y)
	print(slope, intercept, r_value, p_value, stderr)
	return slope, intercept, stderr

def sort_points(list_to_sort, other_list):
	if len(list_to_sort) != len(other_list):
		raise 
	merged_list = [(list_to_sort[i], other_list[i]) for i in range(len(list_to_sort))]
	sorted_list = sorted(merged_list, key=lambda x: x[0])
	return [elem[0] for elem in sorted_list], [elem[1] for elem in sorted_list]

def calculate_Lbol_for_molecule(fluxes, mol):
	Lbol_source = []

	for line in fluxes:
		new_line = []
		for i in range(1,len(line)):
			L_bol = (line[i]*4.0*m.pi*(DIST*3.0857e16**2))/L_sun
			new_line.append(L_bol)
			print(new_line)
		Lbol_source.append(new_line)

	return Lbol_source

def make_log_list(old_list):
	new_list = []
	for elem in old_list:
		if elem != 0:
			new_list.append(m.log10(elem))
		else:
			new_list.append(elem)				

	return new_list

def main():
	data = read_data('SMM_fluxes') 
	fluxes = create_flux_file(data)
	Lbol_source = calculate_Lbol_for_molecule(fluxes, 'CN')
	
	Lbol = [78.7, 4.1, 6.9, 4.4, 3.7, 43.1, 0.2, 10.3, 6.2, 5.7]
	Tbol = [35, 31, 35, 77, 151, 532, 15, 35, 83, 97]

	CN_list = [point[0] for point in Lbol_source]
	HCN_list = [point[1] for point in Lbol_source]
	CS_list = [point[2] for point in Lbol_source]
	Lbol, CN_list = sort_points(Lbol, CN_list)
	Lbol = make_log_list(Lbol)
	CN_list = make_log_list(CN_list)

	a, b, stderr = fit_linear_regression(Lbol, CN_list)
	pearson = calculate_pearson(Lbol, CN_list)
	plot_correlation(Lbol, CN_list, a, b, pearson)
    
	#write_data('CN_Lbol_corr.txt', fluxes, a, b, pearson, stderr)
if __name__ == '__main__':
	main()
