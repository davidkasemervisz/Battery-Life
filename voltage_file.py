import numpy as np
from matplotlib import pyplot as plt
from patch_reader import *

class VoltageFile:
    def __init__(self, filepath):
        with open(filepath, 'r') as file:
            content = file.read().split('\n')
            offset = 0
            self.start_hour = 0
            self.start_minute = 0
            self.start_second = 0
            if content[0].split(': ')[0] == 'Start Hour':
                offset = 3
                self.start_hour = int(content[0].split(': ')[1])
                self.start_minute = int(content[1].split(': ')[1])
                self.start_second = int(content[2].split(': ')[1])

            self.n_samples = int(content[offset].split(': ')[1])
            self.n_timepointsPerSample = int(content[offset + 1].split(': ')[1])
            self.sampling_rate = float(content[offset + 2].split(': ')[1])
            self.resistance = float(content[offset + 3].split(': ')[1])
            self.applied_voltage = float(content[offset + 4].split(': ')[1])
            self.total_time = self.n_samples * self.n_timepointsPerSample / self.sampling_rate

            timepoints = []
            resistor_voltages = []
            power_source_voltages = []

            for sample in range(self.n_samples):
                i_start = 5 + offset + sample * (self.n_timepointsPerSample + 1)
                start_time = int(content[i_start].split(': ')[1])
                for i in range(self.n_timepointsPerSample):
                    timepoints.append(start_time + i / self.sampling_rate)
                    voltages = content[i_start + i + 1].split(", ")
                    resistor_voltages.append(float(voltages[0]))
                    if len(voltages) == 2:
                        power_source_voltages.append(float(voltages[1]))
                    else:
                        power_source_voltages.append(self.applied_voltage)

            self.timepoints = np.asarray(timepoints)
            self.resistor_voltages = np.asarray(resistor_voltages)
            self.power_source_voltages = np.asarray(power_source_voltages)

            self.events = []
            start_index = 5 + offset + self.n_samples * (self.n_timepointsPerSample + 1)
            print("File " + filepath + " events")
            for i in range(start_index, len(content) - 1):
                event = content[i].split(': ')
                name = event[0]
                time = int(event[1])
                print(name + " at time " + event[1] + "s")
                self.events.append(time)

    def analyze_peaks(self):
        threshold = np.max(self.resistor_voltages) * 0.4
        cooldown = 10
        gaps = []
        for sample in range(self.n_samples):
            mask = self.resistor_voltages >= threshold
            start = -1
            for i in range(self.n_timepointsPerSample):
                if mask[i]:
                    if start == -1:
                        start = i
                    else:
                        if i - start > cooldown:
                            gaps.append((i - start) / self.sampling_rate)
                            start = i

        if len(gaps) > 0:
            var = np.var(gaps)
            period = 0
            n_consistentGaps = 0
            average_gap = np.mean(gaps)
            for gap in gaps:
                if abs(gap - average_gap) < var:
                    period += gap
                    n_consistentGaps += 1

            if n_consistentGaps != 0:
                period /= n_consistentGaps

                print(f'Period: {period}s')

            else:
                print('no period detected (a)')

        else:
            print('no period detected (b)')

    def plot_separately(self, patch_data_filepath=None):
        fig, axs = plt.subplots(3)
        current = self.resistor_voltages / self.resistance * 1000
        axs[0].plot(self.timepoints, current)
        axs[0].set_xlabel('Time (s)')
        axs[0].set_ylabel('Current (mA)')
        self.plot_events(axs[0], np.max(current))
        if patch_data_filepath is not None:
            info = read_patch_data(patch_data_filepath, ["Time", "Plot"])
            time = get_time(info[0], self.get_start_time())
            data = info[1]
            axs[0].plot(time, data)
        axs[1].plot(self.timepoints, self.power_source_voltages, color='red')
        axs[1].set_xlabel('Time (s)')
        axs[1].set_ylabel('Voltage (V)')
        self.plot_events(axs[1], np.max(self.power_source_voltages))
        power = self.power_source_voltages * self.resistor_voltages / self.resistance
        axs[2].plot(self.timepoints, power, color='orange')
        axs[2].set_xlabel('Time (s)')
        axs[2].set_ylabel('Power (W)')
        self.plot_events(axs[2], np.max(power))
        plt.show()

    def plot_events(self, ax, max_value):
        for time in self.events:
            ax.plot([time, time], [-max_value/5, 0], color='green')

    def plot_current_and_voltage_together(self):
        fig, ax1 = plt.subplots()
        line1, = ax1.plot(self.timepoints, self.resistor_voltages / self.resistance * 1000, color='blue', label='Current')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Current (mA)')
        ax2 = ax1.twinx()
        line2, = ax2.plot(self.timepoints, -self.power_source_voltages, color='red', label='Voltage')
        ax2.set_ylabel('-Voltage (-V)')
        lines = [line1, line2]
        labels = [line.get_label() for line in lines]
        ax1.legend(lines, labels)
        plt.show()

    def get_start_time(self):
        return self.start_hour * 60 * 60 + self.start_minute * 60 + self.start_second

    def calculate_energy_usage(self):
        if len(self.power_source_voltages) == 0:
            energy_usage = np.sum(self.applied_voltage * self.resistor_voltages) / self.resistance / self.sampling_rate
        else:
            energy_usage = np.sum(self.power_source_voltages * self.resistor_voltages) / self.resistance / self.sampling_rate
        average_power = energy_usage / self.total_time

        print(f'Energy Usage: {energy_usage}J used over a {self.total_time}s time span')
        print(f'Average Power: {average_power}W')
