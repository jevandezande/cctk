import sys
import os
import numpy as np

sys.path.append(os.path.relpath('../cctk'))

from cctk import GaussianOptOutputFile

output_file = GaussianOptOutputFile('cctk/scripts/acetaldehyde.out')

energies = output_file.energies
scf_iter = output_file.scf_iterations
rms_displacements = output_file.rms_displacements
rms_forces = output_file.rms_forces

if output_file.successful: 
    print("Optimization converged!")

print("{0:5} {1:20} {2:20} {3:15} {4:15} {5:20} {6:15}".format("#", "Energy (Hartree)", "Rel Energy (kcal)", "SCF Cycles", "RMS Force", "RMS Displacement", "Distance(2,5)"))

distances = output_file.print_geometric_parameters('distance',2,5)

min_energy = np.min(energies)
for i, energy in enumerate(energies):
    rel_energy = (energy - min_energy) * 627.509 #### convert to kcal
    print("{0:5d} {1:20.5f} {2:20.5f} {3:15d} {4:15.5f} {5:20.5f} {6:15.3f}".format(i+1, energy, rel_energy, scf_iter[i], rms_forces[i], rms_displacements[i], distances[i]))
