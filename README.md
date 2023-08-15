# Soil-Powered Computing::seedling: <br> The Engineer's Guide to _Practical_ SMFC Design:gear:
This is the official repository for practical soil-powered computing. A detailed README is coming soon.

<p align="center">
  <img src="/doc-images/MFC_Figure.png"/>
</p>

## 3D-Printable Soil Microbial Fuel Cells (SMFC)
The `.stl` files for the baseline v0 SMFC and the improved v3.1 SMFC can be found in the `CAD` folder.

Baseline v0 SMFC           |  Improved v3.1 SMFC
:-------------------------:|:-------------------------:
![](/doc-images/v0_Exploded.png)  |  ![](/doc-images/v3.1_Exploded.png)

## Trace-based Computing Runtime Simulation
The trace-based runtime simulation uses real-life SMFC power traces and the user's desired computing systems' datasheet values to estimate the number of possible computing operations one can achieve in a day given the SMFC's energy level. See `Runtime_Simulation/models.py` for how the model is constructed, `Runtime_Simulation/SMFC.py` and the `.csv` files in `Data` for how to format the input SMFC data correctly for the program, `Runtime_Simulation/main.py` to run the simulation and generate the graphs, and `Runtime_Simulation/visualizations.py` to tune the visualization graphs (see below).

<p align="center">
  <img src="/doc-images/Speculative_Design.png"/>
</p>

<p align="center">
  <img src="/doc-images/min_adv_subplots.png"/>
</p>

<p align="center">
  <img src="/doc-images/MARS_on_off.png"/>
</p>
