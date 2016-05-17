# coding: utf-8

from __future__ import division, print_function, unicode_literals, absolute_import

from pymatgen import Structure

"""
This module defines functions that generate workflows for Spin-Orbit calculations.
"""


from fireworks import Workflow
import os
from pymatgen.io.vasp.sets import MPVaspInputSet

from monty.serialization import loadfn
from matmethods.utils.loaders import get_wf_from_spec_dict


__author__ = 'Kiran Mathew'
__credits__ = 'Anubhav jain, Shyue Ping Ong'
__email__ = 'ajain@lbl.gov, kmathew@lbl.gov'


def get_wf_spinorbit_coupling(structure, magmom=None, saxis=(0, 0, 1), vasp_input_set=None,
                              vasp_cmd="vasp", vasp_ncl="vasp_ncl", db_file=None):
    """
    Return Spin-Orbit coupling workflow consisting of 3 fireworks:

    Firework 1 : write vasp input set for structural relaxation,
                 run vasp,
                 pass run location,
                 database insertion.

    Firework 2 : copy files from previous run,
                 write vasp input set for static run,
                 run vasp,
                 pass run location
                 database insertion.

    Firework 3 : copy files from previous run,
                 write vasp input set for SOC
                 run vasp,
                 pass run location
                 database insertion.

    Args:
        structure (Structure): input structure to be relaxed.
        magmom (list): list of magnetic moments for each site
        saxis (tuple): field direction
        vasp_cmd (string): path to normal vasp binary.
        vasp_ncl (string): path to non-collinear vasp binary.
        vasp_input_set (DictVaspInputSet): vasp input set.
        db_file (string): path to file containing the database credentials.

    Returns:
        Workflow
     """

    d = loadfn(os.path.join(os.path.dirname(__file__), "spinorbit_coupling.yaml"))

    v = vasp_input_set or MPVaspInputSet(force_gamma=True)
    d["fireworks"][0]["params"] = {"vasp_input_set": v.as_dict(), "vasp_cmd": vasp_cmd}
    d["fireworks"][1]["params"] = {"vasp_cmd": vasp_cmd}
    d["fireworks"][2]["params"] = {"magmom": magmom, "saxis": saxis, "vasp_cmd": vasp_ncl}

    d["common_params"] = {
        "db_file": db_file
    }

    return get_wf_from_spec_dict(structure, d)


if __name__ == "__main__":
    # the structure from vasp wiki example
    fe_monomer = Structure([[1.73, 1.73, 0.0],
                            [-1.73, 1.73, 0.0],
                            [0.0, 0.0, 10.0]],
                           ["Fe"],
                           [[0, 0, 0]])
    wf = get_wf_spinorbit_coupling(fe_monomer, magmom=[3.0], saxis=(0,0,1),
                                   vasp_cmd="srun vasp", vasp_ncl="srun vasp_ncl",
                                   db_file=">>db_file<<")
