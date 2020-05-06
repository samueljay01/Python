import fonctionTP
import matplotlib.pyplot as plt
import numpy as np

################################################
#           Parti traitement des donnees       #
################################################

VexctOpt, temps = fonctionTP.generateOpt()

dataExperimentale = fonctionTP.csvRead('t_ve_vc_oscillo_exp', skiprows=2)
T = dataExperimentale[:, 0]
Ve = dataExperimentale[:, 1]
Vc = dataExperimentale[:, 2]
Vr = dataExperimentale[:, 1] - dataExperimentale[:, 2]
Vet, Vrt, Vct, Vcht, i = fonctionTP.generateNonOpt()

prompt = (input("Taper 1 si vous voulez faire une "
                "generation et acquistion avec la NI-DAQmx: "))

if prompt == '1':
    acquistion = fonctionTP.inputOutputDAQmx(VexctOpt)

################################################
#           Parti graphique                    #
################################################


# Courbe theorique
plt.figure(1)
plt.subplot(211)
plt.plot(i, Vet, 'red', label='excitation non optimise')
plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
plt.ylabel('Amplitude')
plt.xlabel('Time')
plt.legend()
plt.title('Courbe theorique')

plt.subplot(212)
plt.plot(i, Vct, 'red', label='reponse non optimise')
plt.plot(i, Vcht, 'blue', label='decharge capa')
plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
plt.ylabel('Amplitude')
plt.legend()
plt.xlabel('Time')

plt.figure(2)
plt.plot(Vct[2:1000], Vrt[2:1000], "red", label='portait de phase non optimise')
plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
plt.title("Portait de phase")
plt.arrow(Vct[2], Vrt[2], 0.005, 20, head_width=0.1, head_length=10, fc='r', ec='r')
plt.ylabel('Current')
plt.xlabel('Charge')

# Excitation optimise
plt.figure(3)
plt.plot(temps, VexctOpt, 'black', label='excitation optimise')
plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
plt.ylabel('Amplitude')
plt.legend()
plt.xlabel('Time')

# Courbe exprimentaux
plt.figure(4)
plt.subplot(211)
plt.plot(T, Ve, 'red', label='excitation non optimise')
plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
plt.ylabel('Amplitude')
plt.xlabel('Time')
plt.legend()
plt.title('Courbe exprimentaux')

plt.subplot(212)
plt.plot(T, Vc, 'red', label='reponse non optimise')
plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
plt.ylabel('Amplitude')
plt.legend()
plt.xlabel('Time')

plt.figure(5)
plt.plot(Vc[2:1000], Vr[2:1000], "red", label='portait de phase non optimise')
plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
plt.title("Portait de phase expirimentale")
plt.ylabel('Current')
plt.xlabel('Charge')

if prompt == 1:
    plt.figure(6)
    plt.plot(acquistion)
    plt.ylabel('Amplitude')
    plt.xlabel('Time')
    plt.title('Acquistion de la DAQmx')

plt.legend()
plt.show()
