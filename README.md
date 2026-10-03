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

### `revision/`  (calculations added with the revised manuscript)

Same file conventions as above; Kylin runs that were wrapped in an external
memory monitor additionally contain `peakrss.tsv` (elapsed time, `VmRSS`
and `VmHWM` of the process in kB, sampled every 2 s, with the final
`ru_maxrss` in the trailing comment line).  Unless stated otherwise the
Kylin runs use the code version, basis sets, pseudopotentials, grids and
convergence settings of the corresponding calculations above.

- `timing-decomposition/Si{16,32,64,128,256}-HSE06`: the HSE06 scaling
  benchmarks rerun with per-step timers (`SCF.print_time = ON`); source of
  the per-iteration non-exchange timings in SI Table S3.
- `peak-memory/Si{16,32,64,128,256}-HSE06`: the same benchmarks run under
  the memory monitor; source of the resident-set-size rows of SI Table S3
  (`peakrss.tsv`).  `Si256-HSE06-current-version/` is the Si256 run
  repeated with the current code version (quoted in the response letter).
- `kpoint-series/Si-HSE06-k{111,222,333,444,555}-{LSDF,FTDF}`: 2-atom Si
  cell, c_IP = 60, as a function of the k-mesh; SI Table S4.  The 1x1x1
  runs are dispatched to the Gamma-point engine and are not part of the
  table.
- `basis-set-forces/{Si16,MgO16}-HSE06-{basis}-{FTDF,robust,naive}`:
  displaced 16-atom cells in the SZV-SR, DZVP-SR and TZV2P(-SR) MOLOPT
  bases, c_IP = 30; `robust` = three-term gradient formula, `naive` =
  non-robust formula, `FTDF` = reference in the same basis; SI Table S5.
- `cip-16atom/{Si16,BN16,LiH16,CsI16,MgO16}-HSE06/{full,none,ftdf,chol}`:
  c_IP convergence of energies and forces for displaced 16-atom cells
  (`full` = robust fitting on, `none` = off, `ftdf` = reference, as in
  `scaling/cip-Si16-HSE06`); `chol/t{threshold}` selects the interpolation
  points by pivoted Cholesky of the local pair Gram matrix
  (`SCF.lsdf_ipslct = CHOL`) instead of randomized QRCP (Si16, LiH16 and
  MgO16 only).  Response letter, Reviewer 2, major points 2 and 3.
- `gradient-toy/He{1,2}-HSE06-{FTDF,robust,naive}`: one- and two-function
  He test cases for the robust versus non-robust gradient (response letter,
  Reviewer 2, major point 4).
- `cp2k-4c-hfx/`: CP2K four-center HFX runs for the Si supercells of the
  scaling figure (SI Table S9).  `atomic-guess/` = ADMM, atomic guess
  (row a; Si256 on the 2 TB node); `pbe-restart/` = PBE run (`pbe.inp`,
  `pbe.log`) followed by the HSE06 restart with density-matrix screening
  (`cp2k.inp`, `cp2k.log`; row b) -- for Si16 the screened run
  (`Si16-HSE06-screened-unstable/`) did not converge and the entry of the
  table is the unscreened restart in `Si16-HSE06/`; `no-admm/` = the same
  restart protocol without ADMM, i.e. exact exchange in the primary basis
  (row c).  PBE restart wavefunctions are not included.

## Notes

- Kylin total energies are reported in the logs on lines tagged `[ENERG]` as
  `eTotl` (Hartree); the last SCF step is the converged value.
- Absolute total energies of Kylin/PySCF/CP2K versus VASP are not directly
  comparable (different pseudopotentials and basis families); only band gaps
  and energy differences (adsorption energy) are compared across code families.
