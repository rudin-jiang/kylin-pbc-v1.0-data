CP2K four-center HFX + ADMMS/cpFIT3, PBE restart, EPS_SCHWARZ=1e-8
Collected 2026-10-19; status note added 2026-10-22.

STATUS: superseded. The revised manuscript (Fig. 6, SI Table S9) and the
response letter (Table R5) report the EPS_SCHWARZ=1e-6 PBE-restart series
in ../pbe-restart/ as protocol (b), together with the atomic-guess series
(a) in ../atomic-guess/ and the no-ADMM reference (c) in ../no-admm/. The
1e-8 series documented below is retained for reference only; none of its
HSE06 timings or energies enters the manuscript or the response letter.
The only file of this directory used by them is Si16-HSE06/pbe.log, the
historical Si16 PBE stage (identical to
../pbe-restart/Si16-HSE06-screened-unstable/pbe.log) that is added to the
Si16 restart timing. The fig_scaling_time.png and plot_fig_scaling_time.py
kept here draw the superseded 1e-8 curve; the manuscript Fig. 6 and its
script are in ../../kylin-cip6-scaling/figures/.

All five cases use SCREEN_ON_INITIAL_P TRUE, 32 MPI ranks x 1 OpenMP
thread, CP2K 2024.3 (git:6712648), and the cpu32 partition on nominal
512 GB Intel Xeon Gold 6544Y nodes. Si16/32/64 ran on cu04 in jobs
262935/262936/262937. Si128/256 ran on cu08 in job 249374.
The original Kylin and CP2K atomic-guess Si256 figure points remain the
2 TB Xeon Gold 6548N results; the 1e-8 restart curve is all cpu32.

Atoms    HSE06(s)  Historical PBE(s)   Figure total(s)  HSE OT steps
   16     139.291              4.704           143.995             8
   32     242.653             10.929           253.582             8
   64     498.453             21.629           520.082             8
  128    1158.411             41.357          1199.768             9
  256    5734.312             82.587          5816.899             9

Timing convention: the CP2K timer TOTAL TIME / MAXIMUM, excluding launch
overhead, added to the historical PBE time. PBE was not rerun for EPS=1e-8.
The HSE inputs have MAX_MEMORY=12000 MiB/rank for Si16--128 and 8000 for
Si256. Si256 stores 246.782 GiB of ERIs in total and recomputes about 28%
of its ERIs each iteration. Its final MEMORY| Estimated peak process
memory is 15033 MiB. A per-process peak multiplied by 32 is only a rough
rank-multiplier estimate; it does not measure the simultaneous whole-node peak.

Contents and reproducibility

Si*-HSE06/: byte-identical HSE06 cp2k.inp/cp2k.log and historical
  pbe.inp/pbe.log; small cases include the original job evidence.
cp2k-data/: original BASIS_MOLOPT, BASIS_ADMM, BASIS_ADMM_MOLOPT and
  GTH_POTENTIALS from the CP2K installation used for these runs.
job-evidence-small/: original preparation/submission metadata and runner.
job-evidence-large/: original cpu32 submission script and Slurm output.
  These evidence scripts retain their original working paths and, for the
  large job, other calculations executed in the same allocation. They are
  historical records, not scripts to run directly from this archive.
provenance.json: original absolute paths, archive-relative paths and SHA256
  for all copied source files and the referenced historical comparison logs.
SHA256SUMS: hashes of the files in this dataset (excluding itself).
collect_results.py: rebuilds results_eps8.csv and summary_eps8.json from
  archived logs, checking source hashes and normal convergence/completion.
plot_fig_scaling_time.py: the manuscript plotting script; reads the summary
  beside itself and writes fig_scaling_time.png unless --output is supplied.

To re-collect without the temporary benchmark directories, run:
  python3 collect_results.py
Keep this directory in the complete data archive: the collector also reads
../pbe-restart, ../atomic-guess and ../../../scaling for historical comparisons.
To verify the local files, run from this directory:
  sha256sum -c SHA256SUMS
To regenerate the figure in a scratch location:
  python3 plot_fig_scaling_time.py --output /tmp/fig_scaling_time_eps8.png

To rerun a case, create a NEW working directory, copy its cp2k.inp and
pbe.inp and all four files in cp2k-data into that directory, then run the
following under a matching 32-rank cpu32 allocation with the original
CP2K 2024.3 environment and OMP_NUM_THREADS=1:
  mpirun -np 32 cp2k.popt -i pbe.inp > pbe.log 2>&1
  mpirun -np 32 cp2k.popt -i cp2k.inp > cp2k.log 2>&1
The PBE input writes the SiN-PBE-RESTART.wfn expected by the HSE06 input.
Large WFN binaries are omitted. Original small-run WFN hashes are retained
in job-evidence-small/manifest.json and the per-case run_metadata.txt.
Do not run calculations in the archive or overwrite the original outputs.

Interpretation of fields and retained history

peak_memory_per_rank_GiB preserves the prior collector's DBCSR
  "max memory usage/rank" (bytes) divided by 2**30.
cp2k_estimated_peak_process_MiB is the distinct final CP2K MEMORY field.
eri_total_GiB sums ERI storage over all ranks; it is neither of the above.
The external time.txt maxrss_rank0_kib measures the MPI launcher and is not
used as a CP2K peak-memory measurement.

The old ../pbe-restart dataset is preserved as the superseded 1e-6 result;
its Si16 successful reference disables density screening. All five new
1e-8 cases converge with screening enabled. ADMM remains in use: e8--e6
energy differences measure setup sensitivity, not errors against an exact
reference. The raw logs retain periodic-cutoff/non-square-MPI warnings.
The fitted five-point exponents describe these observed timings, not
intrinsic asymptotic scaling across identical hardware and cache settings.
