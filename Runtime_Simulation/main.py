import models
import visualizations
import SMFC

#STEP 1: Import voltage values from v3_Data.csv and get filtered average of v3 and v0 cells
days, v0_avg_v, v3_avg_v  = SMFC.getMFC_data('Data/design_iterations/v3_Data.csv')
for ii in range(len(days)): #turn everything into unit of volts
    v0_avg_v[ii] = v0_avg_v[ii]/1000
    v3_avg_v[ii] = v3_avg_v[ii]/1000

# Calculate average voltage and power in data trace
avg_v0 = sum(v0_avg_v) / len(v0_avg_v)
avg_v3 = sum(v3_avg_v) / len(v3_avg_v)
avg_power_v0 = 1e6*(avg_v0**2)/2000 #2k load, power in uW
avg_power_v3 = 1e6*(avg_v3**2)/2000 #2k load, power in uW

print("Avg. v0: " + str(1000*avg_v0) + " mV" , str(avg_power_v0) + " uW")
print("Avg. v3: " + str(1000*avg_v3) + " mV" , str(avg_power_v3) + " uW")

Analog_on_0 = []
for v in v0_avg_v:
    if v > 0.2:
        Analog_on_0.append(1)
    else:
        Analog_on_0.append(0)

Analog_on_3 = []
for v in v3_avg_v:
    if v > 0.2:
        Analog_on_3.append(1)
    else:
        Analog_on_3.append(0)

#Call simulate function
C0 = [0.007000000000000006, 0.007000000000000006, 0.007000000000000006]
C3 = [0.007000000000000006, 0.007000000000000006, 0.007000000000000006]
Advanced0, Minimal_0, ignore = models.simulate(days, v0_avg_v, C0)
Advanced3, Minimal_3, ignore = models.simulate(days, v3_avg_v, C3)

print(sum(Advanced3)/sum(Advanced0))
print(sum(Minimal_3)/sum(Minimal_0))
print(sum(Analog_on_3)/sum(Analog_on_0))

#generate graphs to visualize data below:
visualizations.bar_subplots_analog(days, Analog_on_0, Analog_on_3)
visualizations.bar_subplots2(Advanced0, Advanced3, Minimal_0, Minimal_3) # generate graph 13
visualizations.bar_subplots(Advanced3, Minimal_3) # generate graph 2