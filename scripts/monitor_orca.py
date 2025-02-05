import sys, cctk
import pandas as pd
from asciichartpy import plot

#### This is a script to monitor the output of Orca files. 
#### In contrast to ``analyze_orca.py``, this script analyzes only one file! 

#### Usage: ``python monitor_orca.py path/to/output.out``

#### Corin Wagen and Eugene Kwan, 2019

filename = sys.argv[1]
print(f"\n\033[3mreading {filename}:\033[0m")

output_file = cctk.OrcaFile.read_file(filename)
if isinstance(output_file, list):
    output_file = output_file[-1]
print(f"{output_file.successful_terminations} successful terminations")
print(f"{output_file.num_imaginaries()} imaginary frequencies")
if output_file.num_imaginaries():
    freqs = [f"{f:.1f} cm-1" for f in output_file.imaginaries()]
    for f in freqs:
        print(f"\t{f}")

print("\n\033[3manalysis:\033[0m")
print(f"{len(output_file.ensemble)} iterations completed")
property_names = ["scf_iterations", "energy", "rms_step", "rms_gradient", "S**2"]

properties = output_file.ensemble[:,property_names]
if len(output_file.ensemble) == 1:
    properties = [properties]
df = pd.DataFrame(properties, columns=property_names).fillna(0)
df["rel_energy"] = (df.energy - df.energy.min()) * 627.509469

print("\n\033[1mENERGY (kcal/mol):\033[0m")
print(plot(df["rel_energy"], {"height": 12, "format": " {:8.2f} "}))

print("\n\033[1mRMS GRADIENT:\033[0m")
print(plot(df["rms_gradient"], {"height": 12, "format": " {:8.6f} "}))

print("\n\033[1mRMS STEP:\033[0m")
print(plot(df["rms_step"], {"height": 12, "format": " {:8.6f} "}))

if df["S**2"][0] is not None:
    print("\n\033[1mSPIN EXPECTATION VALUE:\033[0m")
    print(plot(df["S**2"], {"height": 12, "format": " {:8.6f} "}))

