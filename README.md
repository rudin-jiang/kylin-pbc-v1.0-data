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
submission scripts, job records, and collection/plotting scripts so that this
superseded series and its hardware provenance can be checked.

## Directory to paper mapping

### `internal/`  (Sec. "Internal consistency and gradient verification")

Case naming: `{System}-{XC}-{kmesh}-{engine}`, with System in
{LiH, BN, CsI, MgO, Si} plus Si128, kmesh in {gamma, k333}, engine in
{FTDF, MGDF, LSDF} (`LSDF` is the Kylin-PBC input keyword for the LISDF
exchange engine, `SCF.xchg_method = LSDF`).

- PBE rows, MGDF vs FTDF reference: Table `tab:int_pbe`.
- HSE06 rows, LISDF vs FTDF reference: Table `tab:int_hse`.
- Si128 cases (gamma only) provide the 128-atom rows of both tables.

### `extern/`  (Sec. "External comparison and TiO2 application")

Case naming: `{System}-{XC}-{kmesh}-{code}-{method}`.

- PBE cross-code, Kylin (MGDF) / CP2K (GPW) / PySCF (FFTDF): Table `tab:ext_pbe`.
- HSE06 cross-code energies, Kylin (LISDF) / CP2K (ADMM) / PySCF (FFTDF):
  Table `tab:ext_hse`. For the 3x3x3 column, Kylin and PySCF use a `k333`
  k-mesh, while CP2K uses the equivalent 3x3x3 supercell at Gamma
  (`{System}-HSE06-sc333-cp2k-ADMM`).
- HSE06 band gaps, Kylin / PySCF / VASP: Table `tab:ext_gap`
  (`*-HSE06-*-vasp` folders supply the VASP column).

### `scaling/`  (Sec. "Performance", Figs. `fig:scaling` and `fig:cip`)

- `Si{16,32,64,128,256}-{PBE,HSE06}`: total SCF wall-time scaling,
  Figure `fig:scaling`. Each folder contains both the Kylin and the CP2K
  input/output for that cell. The HSE06 Si256 run kept the finite G=0 term
  of the short-range exchange kernel instead of the probe-charge Ewald
  correction used for Si16--Si128 (`SCF.xchg_exxdiv = NONE`,
  `SCF.xchg_dropG0 = OFF` in its log; all other settings are identical).
  This lowers its total energy by 17 mHa per cell (-1007.779292 instead of
  -1007.762042 Ha) and does not affect the timing (SI Table S9, note e).
  The same calculation with the Ewald correction is
  `revision/peak-memory/Si256-HSE06/`; see also *Exchange G=0 convention*
  under Notes.
- `cip-Si16-HSE06/{ftdf,full,none}/`: LISDF energy convergence with the
  interpolation-point oversampling c_IP, Figure `fig:cip`
  (`full` = robust fitting on, `none` = robust fitting off, `ftdf` = reference).

### `bandgap-TiO2-rutile/`  (Sec. "TiO2 band gap")

- `HSE06-lsdf-c60/`: Kylin HSE06 band gap (LISDF, c_IP = 60).
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
- `kylin-cip6-scaling/`: the c_IP = 6 series of the revised scaling
  comparison (`cases/Si{16,32,64,128,256}_selected_c06/`, run with the
  current build on a 512 GB cpu32 node), the Si64 c_IP = 30 and FFTDF
  controls of the same build (`controls/`), the historical FFTDF references
  (`reference-fftdf-historical/`), `table_values.csv` with both Kylin blocks
  of SI Table S9 / response Table R5, and the Fig. 6 plotting script with
  its raw-log provenance (`figures/`). Source of the c_IP = 6 rows of
  Table S9 and of the Kylin c_IP = 6 curve of Fig. 6; see its `README.txt`.
- `cp2k-4c-hfx/`: CP2K four-center HFX (libint integrals) runs for the Si
  supercells of the scaling figure; source of the CP2K rows of SI Table S9
  and response Table R5 and of the two CP2K HSE06 curves of Fig. 6. All
  runs use 32 MPI ranks x 1 OpenMP thread on one node: the atomic-guess
  Si256 run on the 2 TB Xeon Gold 6548N node, all others on nominal 512 GB
  Xeon Gold 6544Y (cpu32) nodes. Protocol labels follow Table S9.
  - `atomic-guess/Si{N}-HSE06`: protocol (a), ADMM (ADMMS, cpFIT3), atomic
    guess, `EPS_SCHWARZ=1e-6`.
  - `pbe-restart/Si{N}-HSE06`: protocol (b), ADMM, restart from a PBE
    wavefunction with density-matrix screening (`SCREEN_ON_INITIAL_P TRUE`),
    `EPS_SCHWARZ=1e-6`; the PBE-restart series of Fig. 6. Tabulated and
    plotted times include the PBE stage (`pbe.inp`/`pbe.log`). The screened
    Si16 optimization was unstable, so `Si16-HSE06/` holds the
    `SCREEN_ON_INITIAL_P FALSE` result used in the table and the figure; the
    unstable screened run is kept in `Si16-HSE06-screened-unstable/`, whose
    `pbe.log` (identical to `pbe-restart-eps8/Si16-HSE06/pbe.log`) is the
    PBE stage counted in the Si16 restart time. All ERIs were kept in memory
    (`MAX_MEMORY=12000` MiB/rank for Si16--Si128, 5000 for Si256).
  - `no-admm/Si{16,32,64}-HSE06`: protocol (c), restart from the same PBE
    wavefunctions with screening, exchange in the primary basis (no ADMM),
    `EPS_SCHWARZ=1e-6`; the within-CP2K reference for the (a)-(c) and
    (b)-(c) energy differences of Table S9 and for the c_IP calibration
    described in `kylin-cip6-scaling/README.txt`.
  - `pbe-restart-eps8/`: a superseded variant of protocol (b) with
    `EPS_SCHWARZ=1e-8` (all five sizes, screening enabled including Si16),
    retained for reference together with its submission scripts, job
    records, collector and figure script (see its `README.txt`). Apart from
    the Si16 PBE log noted above, it is not used for any number or figure of
    the revised manuscript or the response letter.

  PBE restart wavefunctions are not included; regenerate them from the
  archived PBE inputs.

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
  `scaling/Si{N}-HSE06/` for N = 16--128; the Si256 reruns use the Ewald
  G=0 correction and therefore differ from the June Si256 run by the
  constant shift described under `scaling/`).
- *Current build* (17 October 2026, sha256
  `14bc8db355154879b8dd83c8b3480fa725d9a3e8be9a54cb24784d6c41b243f9`, also
  recorded in `revision/kylin-cip6-scaling/source-records/manifest.json`):
  `revision/kylin-cip6-scaling/` only (c_IP = 6 production series, Si64
  c_IP = 30 control, Si64 FFTDF control). It differs from the submitted
  build in the memory management of the one-time LISDF build phase and in
  other implementation details (fused TILE kernels); algorithm,
  interpolation points, grids and energies are unchanged
  (`controls/Si64_c30/` reproduces `scaling/Si64-HSE06/` to 1e-8 Ha, in
  59.16 s instead of 89.17 s).
- `revision/peak-memory/Si256-HSE06-current-version/` was run with an
  intermediate build (13 July 2026, sha256
  `643bdf76ac5bc3b8a4cc4ed2e41720efe768faad4f56956abaf148fc54b11c03`) whose
  energies differ from both builds above by about 1 microHa/atom; it is not
  used for any number in the manuscript or the response letter.

## Notes

- Kylin total energies are reported in the logs on lines tagged `[ENERG]` as
  `eTotl` (Hartree); the last SCF step is the converged value.
- Exchange G=0 convention: unless stated otherwise, the Kylin HSE06 runs
  replace the finite G=0 limit of the short-range exchange kernel by the
  probe-charge Ewald (Madelung) correction, `SCF.xchg_exxdiv = EWALD` with
  `SCF.xchg_dropG0 = ON` (Sec. 2.2 of the paper); the settings are printed
  at the top of every `kylin-pbc.log`. Runs that retain the finite G=0 term
  (`NONE`/`OFF`): `scaling/Si256-HSE06/` (see the `scaling/` section); the
  self-contained comparisons `scaling/cip-Si16-HSE06/` and
  `revision/gradient-toy/` (LISDF versus FFTDF reference) and `fd-verify/`
  (analytical versus finite-difference forces), in which all runs of a
  comparison share the same setting so that the reported differences are
  unaffected; and `bandgap-TiO2-rutile/HSE06-lsdf-c60/`
  (June 2026 build, `SCF.xchg_exxdiv = NONE`). The two settings differ by a
  constant shift of the exchange energy that decreases with cell size
  (17 mHa per cell for Si256).
- Absolute total energies of Kylin/PySCF/CP2K versus VASP are not directly
  comparable (different pseudopotentials and basis families); only band gaps
  and energy differences (adsorption energy) are compared across code families.
