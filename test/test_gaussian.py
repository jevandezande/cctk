import unittest, sys, os, io, copy
import numpy as np
import cctk

class TestGaussian(unittest.TestCase):
    def test_read_gjf_file(self):
        path = "test/static/gaussian_file.gjf"
        file = cctk.GaussianFile.read_file(path)
        self.assertEqual(file.route_card, "#p opt freq=noraman m062x/6-31g(d) scrf=(smd,solvent=diethylether)")
        self.assertListEqual(file.job_types, [cctk.GaussianJobType.OPT, cctk.GaussianJobType.FREQ, cctk.GaussianJobType.SP])
        self.assertDictEqual(file.link0, {"mem": "1GB", "chk": "test.chk"})
        self.assertEqual(file.title, "title")
        self.assertEqual(file.footer, None)

        mol = file.get_molecule()
        self.assertTrue(isinstance(mol, cctk.Molecule))
        self.assertEqual(mol.num_atoms(), 31)
        self.assertEqual(mol.charge, 0)
        self.assertEqual(mol.multiplicity, 1)

    def test_title(self):
        path = "test/static/title.out"
        file = cctk.GaussianFile.read_file(path)
        title = file.title
        self.assertEqual(title, "H4,H5:5.280@C1:53.700")

    def test_read_out_file(self):
        path = "test/static/gaussian_file.out"
        file = cctk.GaussianFile.read_file(path, extended_opt_info=True)
        self.assertEqual(file.route_card, "#p opt freq=noraman m062x/6-31g(d) scrf=(smd,solvent=diethylether)")
        self.assertDictEqual(file.link0, {"mem": "32GB",  "nprocshared": "16"})
        self.assertListEqual(file.job_types, [cctk.GaussianJobType.OPT, cctk.GaussianJobType.FREQ, cctk.GaussianJobType.SP])
        self.assertEqual(file.title, "title")
        self.assertEqual(file.footer, None)
        self.assertTrue(isinstance(file.ensemble, cctk.ConformationalEnsemble))

        for mol, prop in file.ensemble.items():
            self.assertEqual(prop["filename"], path)

        mol = file.get_molecule()
        self.assertTrue(isinstance(mol, cctk.Molecule))
        self.assertEqual(mol.num_atoms(), 31)
        self.assertEqual(mol.charge, 0)
        self.assertEqual(mol.multiplicity, 1)

        self.assertEqual(file.ensemble[0, "max_force"], 0.000034)
        self.assertEqual(file.ensemble[0, "rms_force"], 0.000009)
        self.assertEqual(file.ensemble[0, "max_displacement"], 0.002266)
        self.assertEqual(file.ensemble[0, "rms_displacement"], 0.000547)
        self.assertEqual(file.ensemble[0, "max_gradient"], 0.000048660)
        self.assertEqual(file.ensemble[0, "rms_gradient"], 0.000012560)
        self.assertEqual(file.ensemble[0, "max_internal_force"], 0.000033913)
        self.assertEqual(file.ensemble[0, "rms_internal_force"], 0.000008756)
        self.assertEqual(file.ensemble[0, "predicted_change_in_energy"], float("-5.572519e-08"))

        old_path = "test/static/gaussian_file.gjf"
        new_path = "test/static/new_gjf.gjf"

        file.write_file(new_path, molecule=1, link0={"mem": "1GB", "chk": "test.chk"})

        with open(old_path) as old:
            with open(new_path) as new:
                self.assertListEqual(
                    list(new),
                    list(old)
                )

        os.remove(new_path)

        file = cctk.GaussianFile.read_file("test/static/eliminationTS.out")
        self.assertEqual(file.route_card, "#p opt=modredundant freq=noraman b3lyp/6-31g(d) empiricaldispersion=gd3bj")
        self.assertEqual(file.footer, "B 48 50 F\nB 2 48 F")

    def test_link1_out_file(self):
        path = "test/static/ethane.out"
        f, lines = cctk.GaussianFile.read_file(path, return_lines=True)

        self.assertEqual(len(lines), 3)
        self.assertEqual(len(f), 3)
        self.assertTrue(all(isinstance(file, cctk.GaussianFile) for file in f))

        self.assertListEqual(f[0].job_types, [cctk.GaussianJobType.OPT, cctk.GaussianJobType.FREQ, cctk.GaussianJobType.SP])
        self.assertListEqual(f[1].job_types, [cctk.GaussianJobType.NMR, cctk.GaussianJobType.SP])
        self.assertListEqual(f[2].job_types, [cctk.GaussianJobType.NMR, cctk.GaussianJobType.SP])


    def test_write_ensemble(self):
        path = "test/static/gaussian_file.out"
        file = cctk.GaussianFile.read_file(path)
        ense = file.ensemble

        old_path = "test/static/ensemble.gjf"
        new_path = "test/static/new_ensemble.gjf"
        cctk.GaussianFile.write_ensemble_to_file(new_path, ense, "#p opt freq=noraman b3lyp/6-31g(d)", print_symbol=True)

        with open(old_path) as old:
            with open(new_path) as new:
                self.assertListEqual(
                    list(new),
                    list(old)
                )

        os.remove(new_path)

    def test_force_extraction(self):
        path = "test/static/dcm_force.out"
        file = cctk.GaussianFile.read_file(path)
        ense = file.ensemble

        self.assertListEqual(list(ense[0, "forces"][1]), [2.672010074,2.672010074,0.0])

    def test_charges(self):
        path = "test/static/dcm_force.out"
        file = cctk.GaussianFile.read_file(path)
        ense = file.ensemble
        self.assertEqual(ense[-1, "mulliken_charges"][1], -0.051271)

        path = "test/static/h2o.out"
        file = cctk.GaussianFile.read_file(path)
        ense = file.ensemble
        self.assertEqual(ense[-1, "hirshfeld_charges"][1], -0.312885)
        self.assertEqual(ense[-1, "hirshfeld_spins"][1], 0)

        path = "test/static/diiron_complex.out"
        file = cctk.GaussianFile.read_file(path)
        self.assertEqual(file.get_molecule().multiplicity, 11)

    def test_dipole(self):
        path = "test/static/dcm_force.out"
        file = cctk.GaussianFile.read_file(path)
        ense = file.ensemble
        self.assertEqual(ense[-1, "dipole_moment"], 0.3316)


if __name__ == '__main__':
    unittest.main()
