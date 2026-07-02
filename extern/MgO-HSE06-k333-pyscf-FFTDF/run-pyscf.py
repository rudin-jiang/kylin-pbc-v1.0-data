#!/usr/bin/env python3
# PySCF input for MgO-HSE06-k333 (external benchmark)
# Engine: FFTDF (default with_df); basis/pseudo match kylin & CP2K.
import time, os
import pyscf.pbc.gto as pbcgto
import pyscf.pbc.dft as pbcdft

tic = time.time()

cell = pbcgto.Cell()
cell.a = """
        0.0000000000     2.1085000000     2.1085000000
        2.1085000000     0.0000000000     2.1085000000
        2.1085000000     2.1085000000     0.0000000000
"""
cell.atom = """
    Mg      0.0000000000     0.0000000000     0.0000000000
    O       2.1085000000     2.1085000000     2.1085000000
"""
cell.basis = "gth-dzvp-molopt-sr"
cell.pseudo = "gth-pbe"
cell.unit = "A"
cell.precision = 1e-10
cell.verbose = 4
cell.build()

kpts = cell.make_kpts([3, 3, 3])
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
