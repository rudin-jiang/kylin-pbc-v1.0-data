Kylin-PBC c_IP=6 scaling: source archive for the SI table and Fig. 6
=================================================================

Original suite (absolute path):
/home/rudin/code/kylin-pbc/tmp_bench/accuracy_matched_eps6_20261020
Archive created (UTC): 2026-10-20T05:00:02.008110+00:00

Scope and files
---------------
* cases/SiN_selected_c06/: all five production inputs and raw outputs for
  N=16,32,64,128,256, including run_metadata.json, GNU time -v time.txt,
  and exitcode.txt. All five converged and exited with code zero.
* controls/Si64_FTDF/: current, same-binary FFTDF reference at gmesh=0.5.
* controls/Si64_c30/: current c_IP=30 Si64 control; it is distinct from the
  historical c_IP=30 curve and its timing is not substituted into that curve.
* reference-fftdf-historical/SiN-HSE06/: original FFTDF calc.txt, cell.txt,
  and kylin-pbc.log for N=16,32,64,128. All these logged references use
  gmesh=0.6.
* source-records/: exact copies of the original suite summary.json,
  selected.json, calibration.csv, results.csv and manifest.json. Their
  absolute paths retain the original run locations and are not rewritten
  to pretend that every referenced file is in this archive.
* table_values.csv: ten rows (historical c_IP=30 and current c_IP=6 for
  each size), preserving total time, energy, iterations, memory source,
  signed energy difference, and the precise reference used.
* figures/: the six-curve manuscript Fig. 6 in PNG/PDF/SVG, the plotting
  script, its five-size timing CSV, and raw-log provenance with hashes.
* archive_provenance.json: original absolute paths and hashes for copied
  files. SHA256SUMS covers every archived regular file except itself.

The 30-point Si64 calibration is summarized in source-records, including
its selection evidence. Raw scan logs for c_IP=1..29 are NOT copied here;
only the current c_IP=30 calibration control and the independent final
c_IP=6 production point are retained. The omitted raw logs remain under
/home/rudin/code/kylin-pbc/tmp_bench/accuracy_matched_eps6_20261020/cases/Si64_cNN/.
No executable or frozen basis-resource directory is included here.
The frozen executable and data files remain in the original suite; their
SHA256 values are recorded by source-records/manifest.json.

Executable, settings, and execution
----------------------------------
Binary SHA256:
14bc8db355154879b8dd83c8b3480fa725d9a3e8be9a54cb24784d6c41b243f9
Original executable:
/home/rudin/code/kylin-pbc/tmp_bench/accuracy_matched_eps6_20261020/kylin-pbc.snapshot

HSE06 / DZVP-SR / GTH-PBE, Gamma point, MGDF Coulomb, robust TILE LISDF,
QRCP, m=5, ATOM initial guess, gmesh=0.5, EPS_ENGY=1e-6 Ha,
EPS_DMAT=1e-3. c_IP=6 is fixed for all five new production runs. Input
files and recorded printed settings are authoritative.
SCF.gmesh is a dimensionless grid parameter in (0,1]; it is not a grid
spacing in bohr. Increasing it from 0.5 to 0.6 increases the grid size.
All new controls and production calculations used cpu32 node cu03,
Intel Xeon Gold 6544Y, one process and 32 OpenMP/MKL threads. The
calibration/reference job was 263448; the resumed production job was
263453. All five new sizes, including Si256, ran on the 512-GB cpu32
node. The resumed workflow reused successful calibration outputs.

Total time is the Kylin-PBC main timer. GNU time -v maximum RSS is
converted from reported kbytes (KiB on Linux) to GiB by division by
1048576. For historical c_IP=30, the memory entries
6.6, 22.5, 82.6, 314, 1178 GiB are the rounded values already reported
in the SI from separate memory-monitoring runs. They are not new GNU
time measurements and should not be described as the memory of the
current Si64_c30 control. The captured old memory row is preserved in
source-records/historical_memory_source.txt.

Historical c_IP=30 data already reside in the parent data archive:
../../scaling/Si16-HSE06/ through ../../scaling/Si256-HSE06/.
Those logs are not duplicated here. Their hashes match the historical
sources recorded in the new suite manifest. The historical Si256 run
used a 2-TB node (Intel Xeon Gold 6548N, 32 threads), whereas all current
c_IP=6 production runs used cpu32/Gold 6544Y.

Accuracy definitions and limitations
-----------------------------------
Signed difference = (E_LISDF - E_reference) * 1e6 / N, in microHa/atom.
The CP2K calibration target is the absolute difference between the
historical cpFIT3, EPS_SCHWARZ=1e-6, PBE-restart Si64 result and its
no-ADMM EPS_SCHWARZ=1e-6 control: 212.617938783562500
microHa/atom. It is a within-CP2K approximation difference, not an
absolute physical-method error or a direct total-energy comparison
between programs.

For current c_IP=6 at Si64, the reference is controls/Si64_FTDF/run.log
(same binary and gmesh=0.5); the final production signed difference is
+156.71645719625000 microHa/atom. The independent calibration run gives
+156.71645719578125 microHa/atom; the tiny difference is rounding/parallel
numerical variation and both point to c_IP=6. Selection was based on
absolute error not exceeding the CP2K target, then nearest to the target.

For current c_IP=6 at Si16, Si32 and Si128, table_values.csv uses the
available historical FFTDF references at gmesh=0.6. These references
have a different grid and executable history from the current
calculations; the reported differences therefore are NOT isolated
same-grid LISDF fitting errors. Historical c_IP=30 differences at
Si16/32/64/128 likewise use the historical gmesh=0.6 FFTDF references.
Historical reference energies printed to 8 decimal places limit the
precision of differences involving them. Extra CSV digits preserve
arithmetic provenance and are not claims of additional accuracy.

No Si256 FFTDF reference is available here. Both Si256 difference fields
are deliberately blank. The Si256 c_IP=6 versus c_IP=30 energy difference
must not be interpreted as its LISDF error.

The current executable includes fused TILE and other implementation
changes relative to the historical paper executable. Speed differences
between the two table blocks are not attributable solely to changing
c_IP. Current Si64_c30 is included as a version-matched control.
Historical Si256 uses xchg_dropG0=OFF and xchg_exxdiv=NONE, whereas all
current c_IP=6 points use ON/EWALD. This convention difference is another
reason not to infer Si256 fitting accuracy from the two total energies.

Figure 6: six curves and reproduction
------------------------------------
The four existing curves are Kylin-PBC PBE, CP2K PBE, historical
Kylin-PBC HSE06 (explicitly labelled c_IP=30), and CP2K four-center HSE06
with the atomic guess. Their sources are ../../scaling/ and the sibling
../cp2k-4c-hfx/atomic-guess/ archive. The original-submission RI-HFX curve
is not substituted for the four-center atomic-guess curve.

The two additional curves are:
* CP2K HSE06, cpFIT3, PBE restart at EPS_SCHWARZ=1e-6, using the archived
  ../cp2k-4c-hfx/pbe-restart/ HSE06 and historical PBE logs.
* Current Kylin-PBC HSE06, c_IP=6, using the five cases/ production logs.

CP2K restart times include both PBE and HSE06. The historical Si16 PBE
stage is located in ../cp2k-4c-hfx/pbe-restart-eps8/Si16-HSE06/pbe.log;
its hash is identical to the PBE source recorded for the EPS_SCHWARZ=1e-6
protocol. Reusing that unchanged PBE stage does not substitute an
EPS_SCHWARZ=1e-8 HSE06 result. All plotting inputs are read from the
data archive; reproducing the figure does not require the original
tmp_bench directory or the external CP2K working directories.

The c_IP=30 and c_IP=6 curves use different implementations, as detailed
above. Their speed difference cannot be attributed solely to c_IP.
Open symbols identify the historical Si256 points run on the 2-TB node;
all new c_IP=6 points ran on cpu32. Si64 calibrates the error target, and
the figure makes no claim of a reference-validated Si256 error.

With Python 3, NumPy and Matplotlib available, run from this directory:

  python3 figures/plot_fig_scaling_time.py \
    --output /tmp/kylin-fig6-reproduction/fig_scaling_time.png

The script locates the enclosing kylin-pbc-v1.0-data archive by default.
For another archive location, add:

    --data-dir /path/to/kylin-pbc-v1.0-data

The output directory receives PNG, PDF, SVG, timings CSV, and provenance
JSON. Source-log timers and hashes are checked by the script before
plotting. The copied provenance JSON retains the original manuscript
script path as an origin record; the identical archived script is
figures/plot_fig_scaling_time.py.
