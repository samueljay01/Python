import numpy as np
import math as ms


def generate_signals(tau=0.0002, excitation_frequency=20e+3, e0=5, number_of_samples=10e2):
    # Function that returns the non optimized signals

    # Physics parameters
    excitation_period = 1 / excitation_frequency
    acquisition_time = 20 * excitation_period
    omega_excitation = 2 * ms.pi * excitation_frequency
    omega_excitation_squared = omega_excitation * omega_excitation
    tau_squared = tau * tau  # time constant of the rc circuit
    excitation_angular_frequency = 2 * ms.pi * excitation_frequency

    B = e0 / (1 + (excitation_angular_frequency ** 2) * (tau ** 2))
    A = -B * excitation_angular_frequency * tau
    K = -A

    i = (np.linspace(-0.0005, acquisition_time, number_of_samples))

    excitation_voltage = np.array((i < 2 * acquisition_time) * (i > 0) * e0 * np.sin(omega_excitation * i))

    resistor_voltage = np.array((i < 2 * acquisition_time) * (i > 0) * tau * B * (
            omega_excitation_squared * tau_squared * (omega_excitation * np.sin(omega_excitation * i) - ((1 / tau) *
                                                                                                         np.exp(
                                                                                                             -i / tau))) + omega_excitation * np.cos(
        omega_excitation * i)))

    capacitor_voltage = np.array((i < 2 * acquisition_time) * (i > 0) * (K * np.exp(-i / tau)
                                                                         + A * np.cos(
                omega_excitation * i) + B * np.sin(omega_excitation * i)))

    capacitor_discharge_voltage = np.array((i < 2 * acquisition_time) * (i > 0) * K * np.exp(-i / tau))

    return excitation_voltage, resistor_voltage, capacitor_voltage, capacitor_discharge_voltage, i


def generate_optimized_signals(tau=0.0002, e0=5, sample_frequency=5e-7, number_of_samples=20e2):
    # Function that returns the optimized signals 

    # Physics parameters
    excitation_frequency = 20e3
    excitation_angular_frequency = 2 * ms.pi * excitation_frequency
    excitation_period = 1 / excitation_frequency

    B = e0 / (1 + (excitation_angular_frequency ** 2) * (tau ** 2))
    A = -B * excitation_angular_frequency * tau
    acquisition_time = sample_frequency * number_of_samples

    excitation_time = excitation_period / 4

    time = np.arange(0, acquisition_time, sample_frequency)

    excitation_voltage = B * np.sin(excitation_angular_frequency * excitation_time) + A * np.cos(
        excitation_angular_frequency * excitation_time)

    first_derivative_excitation_voltage = excitation_angular_frequency * B * np.cos(
        excitation_angular_frequency * excitation_time) - excitation_angular_frequency * A * np.sin(
        excitation_angular_frequency * excitation_time)

    second_derivative_excitation_voltage = -excitation_angular_frequency ** 2 * B * np.sin(
        excitation_angular_frequency * excitation_time) - excitation_angular_frequency ** 2 * A * np.cos(
        excitation_angular_frequency * excitation_time)

    alpha3 = 10 / (excitation_time ** 3) * excitation_voltage - 4 / (
            excitation_time ** 2) * first_derivative_excitation_voltage + 1 / (2 * excitation_time) \
             * second_derivative_excitation_voltage
    alpha4 = -15 / (excitation_time ** 4) * excitation_voltage + 7 / (
            excitation_time ** 3) * first_derivative_excitation_voltage - 1 / (excitation_time ** 2) \
             * second_derivative_excitation_voltage
    alpha5 = 6 / (excitation_time ** 5) * excitation_voltage - 3 / (
            excitation_time ** 4) * first_derivative_excitation_voltage + 1 / (2 * excitation_time ** 3) \
             * second_derivative_excitation_voltage

    beta2 = tau * 3 * alpha3
    beta3 = tau * (4 * alpha4 + alpha3)
    beta4 = tau * (5 * alpha5 + alpha4)
    beta5 = tau * alpha5

    optimized_excitation_voltage_1 = e0 * np.sin(excitation_angular_frequency * time)

    optimized_excitation_voltage_2 = beta2 * time ** 2 + beta3 * time ** 3 + beta4 * time ** 4 + beta5 * time ** 5

    optimized_excitation_voltage = (time < acquisition_time) * (time > excitation_time) * \
                                   optimized_excitation_voltage_1 + (time <= excitation_time) * (time > 0) * \
                                   optimized_excitation_voltage_2

    optimized_excitation_voltage = np.concatenate((optimized_excitation_voltage,
                                                   np.zeros(round(0.5 * len(optimized_excitation_voltage)))))

    optimized_excitation_voltage = np.concatenate((np.zeros(round(0.1 * len(optimized_excitation_voltage))),
                                                   optimized_excitation_voltage))

    total_time = acquisition_time * len(optimized_excitation_voltage) / len(time)
    time = np.linspace(0, total_time, len(optimized_excitation_voltage))
    return optimized_excitation_voltage, time


def csv_write(filename, data, delimiter=',', newline='\n'):
    # Function that saves data in a csv format
    np.savetxt(filename + ".csv", data, delimiter=delimiter, newline=newline)


def csv_read(filename, delimiter=',', skip_rows=0):
    # Function that reads and returns from a csv format
    data = np.loadtxt(filename + '.csv', delimiter=delimiter, skiprows=skip_rows)
    return data


def input_output_daqmx(output_signal, output_port="Dev1/ao0", max_output_value=10, min_output_value=-10,
                       input_port="Dev1/ai0", max_input_value=10, min_input_value=-10):
    # Function that controls the input and outputs of a national instrument acquisition card
    import nidaqmx

    with nidaqmx.Task() as output_task, nidaqmx.Task() as input_task:
        output_task.ao_channels.add_ao_voltage_chan(output_port, max_val=max_output_value, min_val=min_output_value)
        input_task.ai_channels.add_ai_voltage_chan(input_port, max_val=max_input_value, min_val=min_input_value)

        output_task.timing.cfg_samp_clk_timing(1e6, samps_per_chan=output_signal.size)

        output_task.write(output_signal)
        input_signal = input_task.read(5000)

        output_task.start()
        input_task.start()

        output_task.wait_until_done()
        input_task.wait_until_done()

        return input_signal
