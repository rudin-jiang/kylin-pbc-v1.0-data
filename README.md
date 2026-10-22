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
The `revision/cp2k-4c-hfx/pbe-restart-eps8/` dataset additionally retains
submission scripts, job records, and collection/plotting scripts so that the
replacement timing curve and its hardware provenance can be checked.

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
  repeated with an intermediate build (see *Program builds* below); it is
  not used for any number in the manuscript or in the response letter.
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
  scaling figure (SI Table S9 and response Table R5). `atomic-guess/` =
  ADMM, atomic guess, `EPS_SCHWARZ=1e-6` (row a; Si256 on the 2 TB node).
  **`pbe-restart-eps8/` supplies the current PBE-restart curve and row b:**
  all five Si16--Si256 HSE06 runs use `EPS_SCHWARZ=1e-8`,
  `SCREEN_ON_INITIAL_P TRUE`, and ADMMS/cpFIT3, on the cpu32 partition
  (32 MPI ranks x 1 OpenMP thread, nominal 512 GB nodes). Every case
  includes the raw `cp2k.inp`/`cp2k.log` and the historical
  `pbe.inp`/`pbe.log`; total times include both stages, although the PBE
  stage was not rerun for the tighter screening. The dataset also includes
  `results_eps8.csv`, `summary_eps8.json`, a collector reading only the
  archive, source hashes, job records, and the figure script; see its
  `README.txt`. `pbe-restart/` supplies the additional `EPS_SCHWARZ=1e-6`
  PBE-restart results in row d of SI Table S9 and response Table R5;
  Fig. 6 continues to use row b. Row d uses ADMMS/cpFIT3 and includes
  the PBE-stage time. Density-matrix screening is enabled for Si32--Si256;
  Si16 uses the stable `SCREEN_ON_INITIAL_P FALSE` result in `Si16-HSE06/`.
  The excluded screened Si16 HSE06 run is retained in
  `Si16-HSE06-screened-unstable/`, together with the valid PBE input and
  output used for the Si16 restart timing. All row-d runs used 32 MPI
  ranks x 1 OpenMP thread on nominal 512 GB Xeon Gold 6544Y nodes and
  retained their integrals in memory (`MAX_MEMORY=12000` MiB/rank for
  Si16--Si128 and 5000 MiB/rank for Si256).
  `no-admm/` retains the comparison
  without ADMM, i.e. exchange in the primary basis (row c, original
  `EPS_SCHWARZ=1e-6`). PBE restart wavefunctions are not included;
  regenerate them from the archived PBE inputs.

#### Program builds

All Kylin-PBC logs print the version string `Kylin-PBC: v1.0.0`; the builds
are therefore identified by the SHA-256 checksum of the executable.

- *Submitted build* (original submission, June 2026): every Kylin-PBC
  calculation outside `revision/`. The reruns in `revision/` other than
  those listed below were performed with the 2 July 2026 build of the same
  code (sha256
  `523c941a0bcd53a19b027de8e7a25df7d642e8f52b88fd13cca0d546bc1aac67`),
  which uses the same LISDF build-phase code path and reproduces the June
  energies at every SCF step (compare `revision/peak-memory/Si{N}-HSE06/`
  and `revision/timing-decomposition/Si{N}-HSE06/` with
  `scaling/Si{N}-HSE06/`).
- *Current build* (17 October 2026, sha256
  `14bc8db355154879b8dd83c8b3480fa725d9a3e8be9a54cb24784d6c41b243f9`, also
  recorded in `revision/kylin-cip6-scaling/source-records/manifest.json`):
  `revision/kylin-cip6-scaling/` only (c_IP = 6 production series, Si64
  c_IP = 30 control, Si64 FFTDF control). It differs from the submitted
  build only in the memory management of the one-time LISDF build phase;
  algorithm, interpolation points, grids and energies are unchanged
  (`controls/Si64_c30/` reproduces `scaling/Si64-HSE06/` to 1e-8 Ha).
- `revision/peak-memory/Si256-HSE06-current-version/` was run with an
  intermediate build (13 July 2026, sha256
  `643bdf76ac5bc3b8a4cc4ed2e41720efe768faad4f56956abaf148fc54b11c03`) whose
  energies differ from both builds above by about 1 microHa/atom; it is not
  used for any number in the manuscript or the response letter.

## Notes

- Kylin total energies are reported in the logs on lines tagged `[ENERG]` as
  `eTotl` (Hartree); the last SCF step is the converged value.
- Absolute total energies of Kylin/PySCF/CP2K versus VASP are not directly
  comparable (different pseudopotentials and basis families); only band gaps
  and energy differences (adsorption energy) are compared across code families.
