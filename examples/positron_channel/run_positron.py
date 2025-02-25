#!/usr/bin/env python3
#
# Copyright 2022-2023 ImpactX contributors
# Authors: Axel Huebl, Chad Mitchell
# License: BSD-3-Clause-LBNL
#
# -*- coding: utf-8 -*-

import amrex.space3d as amr
from impactx import ImpactX, RefPart, distribution, elements

sim = ImpactX()

# set numerical parameters and IO control
sim.particle_shape = 2  # B-spline order
sim.space_charge = False
# sim.diagnostics = False  # benchmarking
sim.slice_step_diagnostics = False

# domain decomposition & space charge mesh
sim.init_grids()

# load a 10 GeV positron beam with an initial
# normalized rms emittance of 10 nm
energy_MeV = 10.0e3  # reference energy
bunch_charge_C = 190.0e-12  # used with space charge
npart = 10000  # number of macro particles

#   reference particle
ref = sim.particle_container().ref_particle()
ref.set_charge_qe(1.0).set_mass_MeV(0.510998950).set_energy_MeV(energy_MeV)

#   particle bunch
distr = distribution.Triangle(
    sigmaX=5.054566450e-6,
    sigmaY=5.054566450e-6,
    sigmaT=8.43732950e-7,
    sigmaPx=1.01091329e-7,
    sigmaPy=1.01091329e-7,
    sigmaPt=1.0e-2,
    muxpx=0.0,
    muypy=0.0,
    mutpt=0.995037190209989,
)
sim.add_particles(bunch_charge_C, distr, npart)

# add beam diagnostics
monitor = elements.BeamMonitor("monitor", backend="h5")

# design the accelerator lattice)
ns = 1  # number of slices per ds in the element
period = [
    monitor,
    elements.ChrQuad(ds=0.1, k=-6.674941, units=1, nslice=ns),
    elements.ChrDrift(ds=0.3, nslice=ns),
    elements.ChrQuad(ds=0.2, k=6.674941, units=1, nslice=ns),
    elements.ChrDrift(ds=0.3, nslice=ns),
    elements.ChrQuad(ds=0.1, k=-6.674941, units=1, nslice=ns),
    elements.ChrDrift(ds=0.1, nslice=ns),
    elements.ChrAcc(ds=1.8, ez=10871.950994502130424, bz=1.0e-12, nslice=ns),
    elements.ChrDrift(ds=0.1, nslice=ns),
    monitor,
]

sim.lattice.extend(period)

# number of periods through the lattice
sim.periods = 250

# run simulation
sim.evolve()

# clean shutdown
del sim
amr.finalize()
