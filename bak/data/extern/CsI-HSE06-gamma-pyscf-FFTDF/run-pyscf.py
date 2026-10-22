#!/usr/bin/env python3
# PySCF input for CsI-HSE06-gamma (external benchmark)
# Engine: FFTDF (default with_df); basis/pseudo match kylin & CP2K.
# NOTE: verify 'gth-dzvp-molopt-sr' / 'gth-pbe' cover Cs and I in your
#       PySCF install; heavy elements may need an explicit basis/pseudo dict.
import time, os
import pyscf.pbc.gto as pbcgto
import pyscf.pbc.dft as pbcdft

tic = time.time()

cell = pbcgto.Cell()
cell.a = """
        4.5670000000     0.0000000000     0.0000000000
        0.0000000000     4.5670000000     0.0000000000
        0.0000000000     0.0000000000     4.5670000000
"""
cell.atom = """
    Cs      0.0000000000     0.0000000000     0.0000000000
    I       2.2835000000     2.2835000000     2.2835000000
"""
cell.basis = "gth-dzvp-molopt-sr"
cell.pseudo = "gth-pbe"
cell.unit = "A"
cell.precision = 1e-10
cell.verbose = 4
cell.build()

kpts = cell.make_kpts([1, 1, 1])
kmf = pbcdft.KRKS(cell, kpts)
kmf.xc = "HSE06"
kmf.max_cycle = 200
kmf.conv_tol = 1e-7
etot = kmf.kernel()
print("E_tot (Ha) =", etot)

# approximate band gap from k-point eigenvalues
try:
    homo = max(kmf.mo_energy[i][kmf.mo_occ[i] > 0].max() for i in range(len(kpts)))
    lumo = min(kmf.mo_energy[i][kmf.mo_occ[i] == 0].min() for i in range(len(kpts)))
    print("Band gap (eV) =", (lumo - homo) * 27.211386245988)
except Exception as ex:
    print("gap calc skipped:", ex)

print("wall time (s):", time.time() - tic)
print("OMP_NUM_THREADS:", os.getenv("OMP_NUM_THREADS", "not set"))
