import sys, re
import numpy as np

from abc import abstractmethod

from cctk import File, Molecule, ConformationalEnsemble
from cctk.helper_functions import get_symbol, compute_distance_between, compute_angle_between, compute_dihedral_between, get_number


class OrcaFile(File):
    """
    Generic class for all Orca `.inp` and `.out` files.

    Attributes:
        title (str): the title from the file
        ensemble (ConformationalEnsemble): `ConformationalEnsemble` instance
        header (str): file header
    """

    def __init__(self, ensemble, title=None, header=None):
        if ensemble and isinstance(ensemble, ConformationalEnsemble):
            self.ensemble = ensemble
        if title and (isinstance(title, str)):
            self.title = title
        if header and (isinstance(header, str)):
            self.header = header

    @classmethod
    def read_file(cls, filename):
        pass

    def write_file(self, filename, molecule=None, header=None):
        """
        Write a ``.inp`` file, using object attributes. If no header is specified, the object's header will be used.

        Args:
            filename (str): path to the new file
            molecule (int): which molecule to use -- passed to ``self.get_molecule()``.
                Default is -1 (e.g. the last molecule), but positive integers will select from self.ensemble.molecules (0-indexed).
                A ``Molecule`` object can also be passed, in which case that molecule will be written to the file.
            header (str): header for new file
        """
        if molecule is None:
            molecule = -1
        if not isinstance(molecule, Molecule):
            molecule = self.ensemble.molecules[molecule]

        if header is None:
            header = self.header

        self.write_molecule_to_file(filename, molecule, header)

    @classmethod
    def write_molecule_to_file(cls, filename, molecule, header, print_symbol=False):
        """
        Write a ``.inp``file using the given molecule.

        Args:
            filename (str): path to the new file
            molecule (Molecule): which molecule to use -- a``Molecule`` object.
            header (str): header for new file
            print_symbol (Bool): if atomic symbols should be printed instead of atomic numbers
        """
        if not isinstance(molecule, Molecule):
            raise TypeError("need a valid molecule to write a file!")

        if (header is None) or (not isinstance(header, str)):
            raise ValueError("can't write a file without a header")

        text = f"{header.strip()}\n\n"

        text += f"* xyz {int(molecule.charge)} {int(molecule.multiplicity)}\n"
        for index, Z in enumerate(molecule.atomic_numbers, start=1):
            line = molecule.get_vector(index)
            if print_symbol:
                Z = get_symbol(Z)
                text += f"{Z:>2}       {line[0]:>13.8f} {line[1]:>13.8f} {line[2]:>13.8f}\n"
            else:
                text += f"{Z:2d}       {line[0]:>13.8f} {line[1]:>13.8f} {line[2]:>13.8f}\n"

        text += "*\n"
        text += "\n"

        #### write the file
        super().write_file(filename, text)

    def get_molecule(self, num=None):
        """
        TODO: check indexing here

        Returns the last molecule (from an optimization job or other multi-molecule jobs) or the only molecule (from other jobs).

        If ``num`` is specified, returns that job (1-indexed for positive numbers). So ``job.get_molecule(3)`` will return the 3rd element of ``job.molecules``, not the 4th.
        """
        # some methods pass num=None, which overrides setting the default above
        if num is None:
            num = -1

        if not isinstance(num, int):
            raise TypeError("num must be int")

        #### enforce 1-indexing for positive numbers
        if num > 0:
            num += -1

        return self.ensemble.molecules[num]
