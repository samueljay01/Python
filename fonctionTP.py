import numpy as np
import math as ms
import matplotlib.pyplot as plt
import csv
import nidaqmx as mx


def generateNonOpt(tau=0.0002, Fexc=20e+3, E0=5, Nech=1000):
    # Function that returns the non optimizied signals 
    
    # Physics parameters
    Texc = 1 / Fexc                  
    Tacq = 20 * Texc
    Wexc = 2 * ms.pi * Fexc
    Wexc2 = Wexc * Wexc
    tau2 = tau * tau
    pulsExc = 2 * ms.pi * Fexc

    B = E0 / (1 + (pulsExc ** 2) * (tau ** 2))
    A = -B * pulsExc * tau
    K = -A
    i = (np.linspace(-0.0005, Tacq, Nech)) # Number of points used in the simulation

    Vet = np.array((i < 2 * Tacq) * (i > 0) * E0 * np.sin(Wexc * i))   # excitation signal
    Vrt = np.array((i < 2 * Tacq) * (i > 0) * tau * B * (              # signal on the edges of the resistor
            Wexc2 * tau2 * (Wexc * np.sin(Wexc * i) - ((1 / tau) *
            np.exp(-i / tau))) + Wexc * np.cos(Wexc * i)))

    Vct = np.array((i < 2 * Tacq) * (i > 0) * (K * np.exp(-i / tau)    # signal on the edges of the capacitor
            + A*np.cos(Wexc * i) + B*np.sin(Wexc * i)))

    Vcht = np.array((i < 2 * Tacq) * (i > 0) * K * np.exp(-i / tau))   # signal of the capacitor discharging 
    
    return Vet,Vrt,Vct,Vcht,i


def generateOpt(tau=0.0002, E0=5, freqEch=5e-7, nbPoints=20e2):
    # Function that returns the  optimizied signals 
    
    # Physics parameters
    freqExc = 20e3
    pulsExc = 2 * ms.pi * freqExc
    periodeExc = 1 / freqExc
    B = E0 / (1 + (pulsExc ** 2) * (tau ** 2))
    A = -B * pulsExc * tau
    acqTime = freqEch * nbPoints

    tempsExc = periodeExc / 4

    temps = np.arange(0, tempsAcq, freqEch)

    Vcpt = B * np.sin(pulsExc * tempsExc) + A * np.cos(pulsExc * tempsExc)
    d1Vcpt = pulsExc * B * np.cos(pulsExc * tempsExc) - pulsExc * A * np.sin(pulsExc * tempsExc)
    d2Vcpt = -pulsExc ** 2 * B * np.sin(pulsExc * tempsExc) - pulsExc ** 2 * A * np.cos(pulsExc * tempsExc)

    alpha3 = 10 / (tempsExc ** 3) * Vcpt - 4 / (tempsExc ** 2) * d1Vcpt + 1 / (2 * tempsExc) * d2Vcpt
    alpha4 = -15 / (tempsExc ** 4) * Vcpt + 7 / (tempsExc ** 3) * d1Vcpt - 1 / (tempsExc ** 2) * d2Vcpt
    alpha5 = 6 / (tempsExc ** 5) * Vcpt - 3 / (tempsExc ** 4) * d1Vcpt + 1 / (2 * tempsExc ** 3) * d2Vcpt

    beta2 = tau * 3 * alpha3
    beta3 = tau * (4 * alpha4 + alpha3)
    beta4 = tau * (5 * alpha5 + alpha4)
    beta5 = tau * alpha5

    VExcOpt1 = E0 * np.sin(pulsExc * temps)
    VExcOpt2 = beta2 * temps ** 2 + beta3 * temps ** 3 + beta4 * temps ** 4 + beta5 * temps ** 5

    VExcOpt = (temps < tempsAcq) * (temps > tempsExc) * VExcOpt1 \
              + (temps <= tempsExc) * (temps > 0) * VExcOpt2

    VExcOpt = np.concatenate((VExcOpt, np.zeros(round(0.5 * len(VExcOpt)))))
    VExcOpt = np.concatenate((np.zeros(round(0.1 * len(VExcOpt))), VExcOpt))

    totalTime = tempsAcq*len(VExcOpt)/len(temps)
    temps = np.linspace(0,totalTime,len(VExcOpt))
    return VExcOpt,temps


def csvWrite(filename, data, delimter=',', newline='\n'):
    np.savetxt(filename + ".csv", data, delimiter=delimter, newline=newline)


def csvRead(filename, delimter=',', skiprows=0):
    data = np.loadtxt(filename + '.csv', delimiter=delimter, skiprows=skiprows)
    return data

def inputOutputDAQmx(outputSignal, outputPort="Dev1/ao0", outMaxVal=10, outMinVal=-10,
            inputPort="Dev1/ai0", inMaxVal=10, inMinVal=-10):

    import nidaqmx

    with nidaqmx.Task() as task, nidaqmx.Task() as task2:

        task.ao_channels.add_ao_voltage_chan(outputPort, max_val=outMaxVal, min_val=outMinVal)
        task2.ai_channels.add_ai_voltage_chan(inputPort, max_val=inMaxVal, min_val=inMinVal)

        task.timing.cfg_samp_clk_timing(1e6, samps_per_chan=signalOpt.size)

        #signalOpt = fonctions.generateOpt(2e-4)

        task.write(outputSignal)
        inputSignal = task2.read(5000)

        task.start()
        task2.start()

        task.wait_until_done()
        task2.wait_until_done()

        return inputSignal



