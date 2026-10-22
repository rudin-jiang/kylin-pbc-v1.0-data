# Data for "Kylin-pbc: A Gaussian-Type Orbital Periodic DFT Program with Low-Scaling Exact Exchange"

This directory holds the input and output files for every calculation reported
in the manuscript. The layout mirrors the working tree in `art/example/`, and
only the cases actually used in the paper are included. It was produced by
`art/example/collect_paper_data.py`.

## File conventions

| Code | Input files | Output files |
|---|---|---|
| Kylin-pbc | `cell.txt`, `calc.txt` | `kylin-pbc.log` (`kylin-pbc.err` if non-empty) |
| CP2K | `cp2k.inp` | `cp2k.log` |
| PySCF | `run-pyscf.py` | `pyscf.log` |
| VASP | `INCAR`(`.hse`/`.pbe`), `KPOINTS`, `POSCAR` | `OUTCAR`, `OSZICAR`, `vasprun.xml`, `EIGENVAL`, `bandgap.txt` |

Excluded on purpose: VASP `POTCAR` (redistribution is not permitted under the
VASP license), large restart binaries (`WAVECAR`, `CHG`, `CHGCAR`), scheduler
and helper scripts (`slurm-*`, `submit*`, `run*.slurm`, `*.sh`, generators), and
intermediate/backup variants (`*.pre-scaling`, `*.g05orig`, `*.prev`, `*.bak`,
`kylin-pbc-fix.*`, `*.ewald-nogap`).

## Directory to paper mapping

### `internal/`  (Sec. "Internal consistency and gradient verification")

Case naming: `{System}-{XC}-{kmesh}-{engine}`, with System in
{LiH, BN, CsI, MgO, Si} plus Si128, kmesh in {gamma, k333}, engine in
{FTDF, MGDF, LSDF}.

- PBE rows, MGDF vs FTDF reference: Table `tab:int_pbe`.
- HSE06 rows, local-ISDF (LSDF) vs FTDF reference: Table `tab:int_hse`.
- Si128 cases (gamma only) provide the 128-atom rows of both tables.

### `extern/`  (Sec. "External comparison and TiO2 application")

Case naming: `{System}-{XC}-{kmesh}-{code}-{method}`.

- PBE cross-code, Kylin (MGDF) / CP2K (GPW) / PySCF (FFTDF): Table `tab:ext_pbe`.
- HSE06 cross-code energies, Kylin (LSDF) / CP2K (ADMM) / PySCF (FFTDF):
  Table `tab:ext_hse`. For the 3x3x3 column, Kylin and PySCF use a `k333`
  k-mesh, while CP2K uses the equivalent 3x3x3 supercell at Gamma
  (`{System}-HSE06-sc333-cp2k-ADMM`).
- HSE06 band gaps, Kylin / PySCF / VASP: Table `tab:ext_gap`
  (`*-HSE06-*-vasp` folders supply the VASP column).

### `scaling/`  (Sec. "Performance", Figs. `fig:scaling` and `fig:cip`)

- `Si{16,32,64,128,256}-{PBE,HSE06}`: total SCF wall-time scaling,
  Figure `fig:scaling`. Each folder contains both the Kylin and the CP2K
  input/output for that cell.
- `cip-Si16-HSE06/{ftdf,full,none}/`: local-ISDF energy convergence with the
  interpolation-point oversampling c_IP, Figure `fig:cip`
  (`full` = robust fitting on, `none` = robust fitting off, `ftdf` = reference).

### `bandgap-TiO2-rutile/`  (Sec. "TiO2 band gap")

- `HSE06-lsdf-c60/`: Kylin HSE06 band gap (local-ISDF, c_IP = 60).
- `PBE/`: Kylin PBE band gap.
- `vasp-ref/`: plane-wave VASP (PAW) HSE06 and PBE reference gaps.

### `adsorption-Pt100-CO/`  (Sec. "CO adsorption on Pt(100)", Table `tab:ptco`)

- `CO/`, `Pt100/`, `Pt100-CO/`: the three Kylin HSE06 single points that give
  the adsorption energy E_ads = E(Pt100) + E(CO) - E(Pt100-CO).
- `vasp-ref/`: the corresponding VASP (PAW) reference energies.

### `fd-verify/`  (Sec. "Finite-difference gradient verification")

- `Si/` and `MgO/`, each with `base/` plus `xp,xm,yp,ym,zp,zm/`: analytical
  forces checked against central finite differences from +/-0.001 Bohr
  displacements of the second atom.

## Notes

- Kylin total energies are reported in the logs on lines tagged `[ENERG]` as
  `eTotl` (Hartree); the last SCF step is the converged value.
- Absolute total energies of Kylin/PySCF/CP2K versus VASP are not directly
  comparable (different pseudopotentials and basis families); only band gaps
  and energy differences (adsorption energy) are compared across code families.
