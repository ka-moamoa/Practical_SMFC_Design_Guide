import math
from matplotlib import pyplot as plt

def internal_R_v3(R=2000): #return internal resistance of v3 cells in ohms
    #https://www.jstage.jst.go.jp/article/jwet/20/1/20_21-087/_pdf
    v0_oc = 48.5e-3 #48.5 mV
    v0_cc = 4.8e-3
    v0_r = R*((v0_oc/v0_cc)-1)

    v1_oc = 43.8e-3
    v1_cc = 20.9e-3
    v1_r = R*((v1_oc/v1_cc)-1)

    v2_oc = 45.2e-3
    v2_cc = 23.5e-3
    v2_r = R*((v2_oc/v2_cc)-1)

    return (v0_r+v1_r+v2_r)/3

def internal_R_v0(R=2000): #return internal resistance of v0 cells in ohms
    v3_oc = 41.7e-3 #41.7mV
    v3_cc = 5.1e-3
    v3_r = R*((v3_oc/v3_cc)-1)

    v4_oc = 48.7e-3
    v4_cc = 16.8e-3
    v4_r = R*((v4_oc/v4_cc)-1)

    v5_oc = 39.1e-3
    v5_cc = 16.9e-3
    v5_r = R*((v5_oc/v5_cc)-1)

    return (v3_r+v4_r+v5_r)/3

def SMFC_current(v, R):
    return v/R

#MODEL
def cap_leakage(E_cap_tn, timestep):
    #Spec for KEMET T491
    return 0.01e-6 * E_cap_tn * timestep

def Matrix_Power(V, R):
    #efficiency interpolated from https://www.analog.com/media/en/technical-documentation/data-sheets/ADP5091-5092.pdf
    #given I_in = 100 uA and SYS = 3V
    #V is the voltage (V) of the SMFC we captured
    #R is the resistance (ohms) of the load we used to get that voltage trace
    Eta = -292.25665*V**4 + 784.30311*V**3 - 770.71691*V**2 + 342.00502*V + 15.83307
    Eta = Eta/100
    Pmax = (V**2)/R
    Pout = Eta*Pmax
    assert((Eta > 0) & (Eta < 1))
    assert(Pout < 500e-6)
    #print(Pout)
    return Pout

def update_capEnergy(e0, V_applied, R, C, dt):
    # e0: initial energy stored
    # V_applied: voltage from SMFC
    # R: internal resistance of SMFC
    # C: capacitance of capacitor
    # dt: time step since last data point
    e_cap = e0 + Matrix_Power(V_applied, R)*dt - cap_leakage(e0, dt)
    v_cap = math.sqrt(2*e_cap/C)
    if e_cap < 0: #Not charging if leakage is greater than energy
        e_cap = 0
    
    return e_cap, v_cap #output final e and v

def Advanced_energy():
    #Now representing "Advanced"
    #startup time of 2500 ms
    t = 2500e-3
    e = 2.4 * 128e-3 * t
    e_startup = 2.4 * 128e-3 * 5e-3
    return e+e_startup

def Minimal_energy():
    #Now representing "Minimal"
    t = 0.888e-3 #tentative time
    e = 0.9 * 4.8e-3 * t #this uses average current
    e_startup = 0#assume negligible, no known startup time given
    return  e + e_startup

def Analog_energy():
    #Now representing Analog
    t = 1e-3 #estimated operating time
    e = 0.11 * 2.15e-6 * t
    e_startup = 0 #analog device, no startup needed :)
    return e + e_startup

#STEP 3:
# For each day:
#   on_Minimal, on_Advanced, on_Analog = 0
#   For each time step (like every 60 s given our logging freq):
#       - Update the energy in our capacitor (put fcn in models.py) given (1) input voltage, (2) time step, (3) capacitance (prob 10 uF), this will be an integral
#       - Check if energy is enough to turn on (1) 1 uJ load, (2) 10 uJ load, and (3) 20 uJ load (will tweak later to reflect real energy cost of each system)
#       - If so, add to on_Minimal, on_Advanced, and on_Analog and reset capacitor energy to 0 J (might tweak this value)
#   Append on_Minimal, on_Advanced, on_Analog to on_Minimal_list, on_Advanced_list, on_Analog_list. This will be a list of how many sensor readings we are able to take with each of these systems every day given the energy we got
#STEP 4: Visualize the daily # of readings with 3 bar graphs, y axis is # of readings and x axis is days.
#   - Given 3 lists of integer values, plot them on bar graphs

def simulate(t_list, v_list, C_h):
    # t_list: list of decimal time stamps in unit of days (e.g. 71.85893518518519 day), same length as v_list
    # v_list: list of voltage values from SFMC
    # C_h: capacitance of the capacitor being filled up by harvester
    on_Advanced_list = []
    on_Analog_list = []
    on_Minimal_list = []

    #assume capacitor is completely discharged at start
    e_advanced_init = 0 
    e_minimal_init = 0
    e_analog_init = 0

    #Initialize daily sensor reading count
    on_Advanced = 0
    on_Minimal = 0
    on_Analog = 0

    cap_energy_analog = []
    cap_energy_minimal = []
    cap_energy_advanced = []

    cap_v_analog = []
    cap_v_minimal = []
    cap_v_advanced = []

    #for each voltage data point
    for jj in range(1,len(t_list)): #last data point was at 71.85893518518519 day

        t = 24*60*60*(t_list[jj] - t_list[jj-1]) #dt is time since last measurement in seconds

        #update amount of energy in capacitor given v0 output
        E_Advanced, v_advanced = update_capEnergy(e_advanced_init, V_applied=v_list[jj], R=internal_R_v0(), C=C_h[0], dt=t)
        E_Minimal, v_minimal = update_capEnergy(e_minimal_init, V_applied=v_list[jj], R=internal_R_v0(), C=C_h[0], dt=t)
        E_Analog, v_analog = update_capEnergy(e_analog_init, V_applied=v_list[jj], R=internal_R_v0(), C=C_h[0], dt=t)
        
        #Check if we have enough power to turn things on
        if E_Advanced > Advanced_energy():
            on_Advanced = on_Advanced + round(E_Advanced/Advanced_energy())
            E_Advanced = 0 #completely discharge, prob bad assumption will change based on matrix board stat
            v_advanced = 0
            
        if E_Minimal > Minimal_energy():
            on_Minimal = on_Minimal + round(E_Minimal/Minimal_energy())
            E_Minimal = 0 #completely discharge, prob bad assumption will change based on matrix board stat
            v_minimal = 0
            
        if E_Analog > Analog_energy():
            on_Analog = on_Analog + round(E_Analog/Analog_energy())
            E_Analog = 0 #completely discharge, prob bad assumption will change based on matrix board stat
            v_analog = 0

        cap_energy_analog.append(E_Analog)
        cap_energy_minimal.append(E_Minimal)
        cap_energy_advanced.append(E_Advanced)
        cap_v_analog.append(v_analog)
        cap_v_minimal.append(v_minimal)
        cap_v_advanced.append(v_advanced)

        #update start condition for next loop
        e_advanced_init = E_Advanced
        e_minimal_init = E_Minimal
        e_analog_init = E_Analog
        
        if math.trunc(t_list[jj-1]) != math.trunc(t_list[jj]): #if a day ended
            #record the number of sensor reading that day to their respective lists
            on_Advanced_list.append(on_Advanced)
            on_Minimal_list.append(on_Minimal)
            on_Analog_list.append(on_Analog)

            #Reset daily sensor reading count
            on_Advanced = 0
            on_Minimal = 0
            on_Analog = 0

    # #Debugging print and plots
    # '''print("# of readings by Advanced: ", on_Advanced_list)
    # print("# of readings by Minimal: ", on_Minimal_list)
    # print("# of readings by Analog: ", on_Analog_list)
    # fig, axs = plt.subplots(3, 1, figsize=(12, 4), sharex=True)
    # axs[0].plot(t_list[1:], cap_energy_advanced, label="E in Advanced Capacitor")
    # axs[0].plot(t_list[1:], cap_energy_minimal, label="E in Minimal Capacitor")
    # axs[0].plot(t_list[1:], cap_energy_analog, label="E in Analog Capacitor")
    # axs.flat[0].set(ylabel="Energy (J)")
    # axs[1].plot(t_list[1:], cap_v_advanced, label="V of Advanced Capacitor")
    # axs[1].plot(t_list[1:], cap_v_minimal, label="V of Minimal Capacitor")
    # axs[1].plot(t_list[1:], cap_v_analog, label="V of Analog Capacitor")
    # axs.flat[1].set(ylabel="Voltage (V)")
    # axs[2].plot(t_list[1:], v_list[1:], label="SMFC Voltage")
    # axs.flat[2].set(ylabel="SMFC Voltage (V)")
    # # specifying horizontal line type
    # #plt.axhline(y = models.Advanced_energy(), color = 'r', linestyle = '-')
    # #plt.axhline(y = models.Analog_energy(), color = 'r', linestyle = '-.')
    # plt.xlabel("Timeline (Days)")
    # axs[0].legend()
    # axs[1].legend()'''

    return on_Advanced_list, on_Minimal_list, on_Analog_list

def getMax(c_list, input_list):
    max_value = max(input_list)
    i = [index for index, item in enumerate(input_list) if item == max_value][0]
    return i, max_value, c_list[i]