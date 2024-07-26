#include <NIDAQmx.h>
#include <iostream>
#include <vector>
#include <string>
#include <chrono>
#include <fstream>
#include <ctime>
#include <vector>

void CheckError(int32 error) {
    if (DAQmxFailed(error)) {
        char errBuff[2048] = { '\0' };
        DAQmxGetExtendedErrorInfo(errBuff, 2048);
        std::cerr << "DAQmx Error: " << errBuff << std::endl;
        exit(1);
    }
}

void measureVoltage(std::fstream& outputFile, int n_datapoints, float samplingRate) {
    TaskHandle taskHandle = 0;
    const char* physicalChannels = "Dev1/ai1,Dev1/ai3";
    std::vector<float64> data(n_datapoints * 2);

    CheckError(DAQmxCreateTask("", &taskHandle));
    CheckError(DAQmxCreateAIVoltageChan(taskHandle, physicalChannels, "",
        DAQmx_Val_Cfg_Default, -10.0, 10.0,
        DAQmx_Val_Volts, NULL));
    CheckError(DAQmxCfgSampClkTiming(taskHandle, "", samplingRate,
        DAQmx_Val_Rising, DAQmx_Val_FiniteSamps,
        n_datapoints));
    CheckError(DAQmxStartTask(taskHandle));

    int32 read;
    CheckError(DAQmxReadAnalogF64(taskHandle, n_datapoints, 10.0, DAQmx_Val_GroupByChannel,
        data.data(), data.size(), &read, NULL));

    for (int i = 0; i < read; i++) {
        outputFile << data[i] << ", " << data[i + read] << "\n";
    }

    CheckError(DAQmxClearTask(taskHandle));
}

void voltageProgram(std::string filepath, int n_samples, int n_datapointsPerSample, float samplingRate, float resistance, float appliedVoltage) {
    std::fstream outputFile(filepath);
    
    if (outputFile.is_open()) {
        std::time_t now = std::time(0);
        std::tm localTime;
        localtime_s(&localTime, &now);
        outputFile << "Start Hour: " << localTime.tm_hour << "\n";
        outputFile << "Start Minute: " << localTime.tm_min << "\n";
        outputFile << "Start Second: " << localTime.tm_sec << "\n";

        outputFile << "Samples: " << n_samples << "\n";
        outputFile << "Data Points Per Sample: " << n_datapointsPerSample << "\n";
        outputFile << "Sampling Rate: " << samplingRate << "\n";
        outputFile << "Resistance: " << resistance << "\n";
        outputFile << "Applied Voltage: " << appliedVoltage << "\n";

        auto startTime = std::chrono::high_resolution_clock::now();
        for (int i = 0; i < n_samples; i++) {
            std::cout << "Sample number " << (i+1) << " of " << n_samples << std::endl;
            auto endTime = std::chrono::high_resolution_clock::now();
            float duration = std::chrono::duration_cast<std::chrono::seconds>(endTime - startTime).count();
            outputFile << "Start Time: " << duration << "\n";
            measureVoltage(outputFile, n_datapointsPerSample, samplingRate);
        }

        outputFile.close();
    }

    else {
        std::cerr << "Failed to load file: " << filepath << std::endl;
    }
}

int main() {

    
    int n_samples = 6 * 10;
    int n_datapointsPerSample = 10000;
    float samplingRate = 1000;
    float shuntResistance = 1.3f;
    float appliedVoltage = 1.36f;
    
    
    int measurements = 6 * 2;
    for (int i = 0; i < measurements; i++) {
        std::string filepath = "C://Users//David//source//repos//BatteryLife//Data//7-26 battery experiments//measurement"
            + std::to_string(i) + ".txt";
        std::cout << "Starting Measurement: " << i << std::endl;
        voltageProgram(filepath, n_samples, n_datapointsPerSample, samplingRate, appliedVoltage, shuntResistance);
    }
    
    return 0;
}
