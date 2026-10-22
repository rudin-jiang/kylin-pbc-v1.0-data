#!/bin/bash
# Called by a one-node, 32-MPI-rank cpu32 Slurm allocation.
set -e
case_dir=$1
cd "$case_dir"
exec 9>.run.lock
flock -n 9
if [[ -e cp2k.log || -e exitcode.txt ]]; then
    echo 'Existing run output found; refusing to overwrite it.' >&2
    exit 73
fi

ulimit -s unlimited
source /etc/profile.d/modules.sh
module load cp2k-2024.3/oneapi-2024.2.1
export OMP_NUM_THREADS=1
set -u
set -o pipefail

{
    date -u '+started_utc=%Y-%m-%dT%H:%M:%SZ'
    printf 'job_id=%s\nnode=%s\nmpi_ranks=%s\nomp_threads=%s\n' \
        "$SLURM_JOB_ID" "$(hostname)" "$SLURM_NTASKS" "$OMP_NUM_THREADS"
    printf 'cp2k_executable=%s\n' "$(command -v cp2k.popt)"
    lscpu | sed -n '/Model name:/p'
    sha256sum cp2k.inp *-PBE-RESTART.wfn
} > run_metadata.txt

set +e
/usr/bin/time -o time.txt -f 'wall_seconds=%e\nmaxrss_rank0_kib=%M' \
    mpirun -np 32 cp2k.popt -i cp2k.inp > cp2k.log 2>&1
rc=$?
set -e
printf '%s\n' "$rc" > exitcode.txt
date -u '+finished_utc=%Y-%m-%dT%H:%M:%SZ' >> run_metadata.txt
exit "$rc"
