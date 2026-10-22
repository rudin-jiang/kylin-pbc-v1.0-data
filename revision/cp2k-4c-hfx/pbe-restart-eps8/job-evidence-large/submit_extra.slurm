#!/bin/bash
#SBATCH --job-name=R2p6-extra
#SBATCH --partition=cpu32
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --exclusive
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err

ulimit -s unlimited
source /etc/profile.d/modules.sh
module load cp2k-2024.3/oneapi-2024.2.1
export OMP_NUM_THREADS=1
BASE="$SLURM_SUBMIT_DIR"   # sbatch copies the script to /var/spool, so BASH_SOURCE is useless here
echo "node: $(hostname)  base: $BASE"
cd "$BASE/4c-admm-pbe-noscreen/Si16" && echo "[$(date)] start 4c-admm-pbe-noscreen/Si16/cp2k.inp" && { /usr/bin/time -f "WALLCLOCK 4c-admm-pbe-noscreen/Si16/cp2k.inp %e s  MAXRSS(rank0) %M kB" mpirun -np 32 cp2k.popt -i cp2k.inp &> cp2k.log ; rc=$? ; } ; echo "[$(date)] done  4c-admm-pbe-noscreen/Si16/cp2k.inp rc=$rc"
cd "$BASE/4c-admm-pbe-e8/Si128" && echo "[$(date)] start 4c-admm-pbe-e8/Si128/cp2k.inp" && { /usr/bin/time -f "WALLCLOCK 4c-admm-pbe-e8/Si128/cp2k.inp %e s  MAXRSS(rank0) %M kB" mpirun -np 32 cp2k.popt -i cp2k.inp &> cp2k.log ; rc=$? ; } ; echo "[$(date)] done  4c-admm-pbe-e8/Si128/cp2k.inp rc=$rc"
cd "$BASE/4c-admm-pbe-e8/Si256" && echo "[$(date)] start 4c-admm-pbe-e8/Si256/cp2k.inp" && { /usr/bin/time -f "WALLCLOCK 4c-admm-pbe-e8/Si256/cp2k.inp %e s  MAXRSS(rank0) %M kB" mpirun -np 32 cp2k.popt -i cp2k.inp &> cp2k.log ; rc=$? ; } ; echo "[$(date)] done  4c-admm-pbe-e8/Si256/cp2k.inp rc=$rc"
cd "$BASE/4c-noadmm-pbe/Si16" && echo "[$(date)] start 4c-noadmm-pbe/Si16/cp2k.inp" && { /usr/bin/time -f "WALLCLOCK 4c-noadmm-pbe/Si16/cp2k.inp %e s  MAXRSS(rank0) %M kB" mpirun -np 32 cp2k.popt -i cp2k.inp &> cp2k.log ; rc=$? ; } ; echo "[$(date)] done  4c-noadmm-pbe/Si16/cp2k.inp rc=$rc"
cd "$BASE/4c-noadmm-pbe/Si32" && echo "[$(date)] start 4c-noadmm-pbe/Si32/cp2k.inp" && { /usr/bin/time -f "WALLCLOCK 4c-noadmm-pbe/Si32/cp2k.inp %e s  MAXRSS(rank0) %M kB" mpirun -np 32 cp2k.popt -i cp2k.inp &> cp2k.log ; rc=$? ; } ; echo "[$(date)] done  4c-noadmm-pbe/Si32/cp2k.inp rc=$rc"
cd "$BASE/4c-noadmm-pbe/Si64" && echo "[$(date)] start 4c-noadmm-pbe/Si64/cp2k.inp" && { /usr/bin/time -f "WALLCLOCK 4c-noadmm-pbe/Si64/cp2k.inp %e s  MAXRSS(rank0) %M kB" mpirun -np 32 cp2k.popt -i cp2k.inp &> cp2k.log ; rc=$? ; } ; echo "[$(date)] done  4c-noadmm-pbe/Si64/cp2k.inp rc=$rc"
