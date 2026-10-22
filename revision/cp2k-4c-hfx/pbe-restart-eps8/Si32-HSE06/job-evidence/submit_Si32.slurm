#!/bin/bash
#SBATCH --job-name=cp2k-e8-Si32
#SBATCH --partition=cpu32
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --exclusive
#SBATCH --time=02:00:00
#SBATCH --chdir=/home/rudin/code/kylin-pbc/tmp_bench/cp2k_eps8_small_20261019/cases/Si32
#SBATCH --output=/home/rudin/code/kylin-pbc/tmp_bench/cp2k_eps8_small_20261019/cases/Si32/slurm-%j.out
#SBATCH --error=/home/rudin/code/kylin-pbc/tmp_bench/cp2k_eps8_small_20261019/cases/Si32/slurm-%j.err

exec bash "/home/rudin/code/kylin-pbc/tmp_bench/cp2k_eps8_small_20261019/run_case.sh" "/home/rudin/code/kylin-pbc/tmp_bench/cp2k_eps8_small_20261019/cases/Si32"
