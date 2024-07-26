from voltage_file import *




test = VoltageFile("C://Users//David//source//repos//BatteryLife//Data//7-26 battery experiments//measurement8.txt")
# test.plot_separately(patch_data_filepath="C://Users//David//PycharmProjects//GTech//BatteryPower//Channel1.csv")
test.plot_separately()

# zn_air = VoltageFile("C://Users//David//source//repos//BatteryLife//Data//7-23 battery experiments//Zn_air_battery.txt")
# power_supply = VoltageFile("C://Users//David//source//repos//BatteryLife//Data//7-23 battery experiments//power_supply_14.txt")
# AAA = VoltageFile("C://Users//David//source//repos//BatteryLife//Data//7-23 battery experiments//AAA_battery.txt")
#
# power_supply.plot_separately()
# zn_air.plot_separately()
# AAA.plot_separately()
