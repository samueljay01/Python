import matplotlib.pyplot as plt

import fonctionTP

################################################
#                Data treatment                #
################################################

optimized_excitation_voltage, optimized_time_interval = fonctionTP.generate_optimized_signals()

experimental_data = fonctionTP.csv_read('t_ve_vc_oscillo_exp',skip_rows=2)
experimental_time_interval = experimental_data[:, 0]
experimental_excitation_voltage = experimental_data[:, 1]
experimental_capacitor_voltage = experimental_data[:, 2]
experimental_resistor_voltage = experimental_data[:, 1] - experimental_data[:, 2]

excitation_voltage, resistor_voltage, capacitor_voltage, capacitor_discharge_voltage, time_interval = \
    fonctionTP.generate_signals()

prompt = (input("Enter 1 for the generation and acquisition to be done by the NI-DAQmx card,"
                " otherwise the data will be taken from the csv file: "))

if prompt == '1':
    acquisition = fonctionTP.input_output_daqmx(optimized_excitation_voltage)

################################################
#           Graphical display                  #
################################################


# Theoretical figures
plt.figure(1)
plt.subplot(211)
plt.plot(time_interval, excitation_voltage, 'red', label='Non optimized excitation')
plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
plt.ylabel('Amplitude')
plt.xlabel('Time')
plt.legend()
plt.title('Theoretical figures')

plt.subplot(212)
plt.plot(time_interval, capacitor_voltage, 'red', label='Non optimized response')
plt.plot(time_interval, capacitor_discharge_voltage, 'blue', label='capacitor discharge')
plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
plt.ylabel('Amplitude')
plt.legend()
plt.xlabel('Time')

plt.figure(2)
plt.plot(capacitor_voltage[2:1000], resistor_voltage[2:1000], "red", label='Non optimized phase portrait')
plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
plt.title("Phase portrait")
plt.arrow(capacitor_voltage[2], resistor_voltage[2], 0.005, 20, head_width=0.1, head_length=10, fc='r', ec='r')
plt.ylabel('Current')
plt.xlabel('Charge')

# Optimized excitation
plt.figure(3)
plt.plot(optimized_time_interval, optimized_excitation_voltage, 'black', label='Optimized excitation')
plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
plt.ylabel('Amplitude')
plt.legend()
plt.xlabel('Time')

# Experimental figures
plt.figure(4)
plt.subplot(211)
plt.plot(experimental_time_interval, experimental_capacitor_voltage, 'red', label=' Non optimized excitation')
plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
plt.ylabel('Amplitude')
plt.xlabel('Time')
plt.legend()
plt.title('Experimental figures')

plt.subplot(212)
plt.plot(experimental_time_interval, experimental_capacitor_voltage, 'red', label='Non optimized response')
plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
plt.ylabel('Amplitude')
plt.legend()
plt.xlabel('Time')

plt.figure(5)
plt.plot(experimental_capacitor_voltage[2:1000], experimental_resistor_voltage[2:1000], "red"
         , label='Non optimized phase portrait')
plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
plt.title("Experimental phase portrait ")
plt.ylabel('Current')
plt.xlabel('Charge')

if prompt == 1:
    plt.figure(6)
    plt.plot(acquisition)
    plt.ylabel('Amplitude')
    plt.xlabel('Time')
    plt.title('Acquisition by the NI-DAQmx')

plt.legend()
plt.show()
