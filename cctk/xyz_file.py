import sys
import re
import numpy as np

from abc import abstractmethod

from cctk import File, Molecule
from cctk.helper_functions import get_symbol, compute_distance_between, compute_angle_between, compute_dihedral_between, get_number


class XYZFile(File):
    """
    Generic class for all xyz files.

    Attributes:
        title (str): the title from the file
        molecule (Molecule): `Molecule` instance
    """

    def __init__(self, molecule, title=None):
        if molecule and isinstance(molecule, Molecule):
            self.molecule = molecule
        if title and (isinstance(title, str)):
            self.title = title

    @classmethod
    def read_file(cls, filename):
        """
        Factory method to create new XYZFile instances.
        """
        lines = super().read_file(filename)
        num_atoms = 0

        try:
            num_atoms = int(lines[0])
        except:
            raise ValueError("can't get the number of atoms from the first line!")

        assert num_atoms == (len(lines) - 2), "wrong number of atoms!"

        title = lines[1]

        atoms = [None] * num_atoms
        geometry = [None] * num_atoms

        for index, line in enumerate(lines[2:]):
            pieces = list(filter(None, line.split(" ")))
            try:
                atoms[index] = get_number(pieces[0])
                geometry[index] = [float(pieces[1]), float(pieces[2]), float(pieces[3])]
            except:
                raise ValueError(f"can't parse line {index+2}!")

        molecule = Molecule(atomic_numbers, geometry)
        return XYZFile(molecule, title)

    def write_file(self, filename):
        """
        Write a .xyz file, using object attributes. "title" will be used as the title if none is defined.

        Args:
            filename (str): path to the new file
        """
        text = f"{self.molecule.num_atoms()}\n"
        try:
            text += f"{self.title}\n"
        except:
            text += "title\n"
        for index, line in enumerate(self.molecule.geometry):
            text += "{:2s} {:.8f} {:.8f} {:.8f}\n".format(get_symbol(self.molecule.atomic_numbers[index]), line[0], line[1], line[2])

        super().write_file(filename, text)

