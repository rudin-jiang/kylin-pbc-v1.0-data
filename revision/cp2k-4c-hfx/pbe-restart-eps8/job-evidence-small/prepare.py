#!/usr/bin/env python3
"""Prepare the missing CP2K EPS_SCHWARZ=1e-8 Si16/32/64 restart runs."""
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil

HERE = Path(__file__).resolve().parent
SOURCE = Path('/home/rudin/tmp-review-cp2k')
SIZES = (16, 32, 64)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    with (SOURCE / 'results.csv').open() as handle:
        old_results = list(csv.DictReader(handle))
    cases = []
    for n in SIZES:
        original = SOURCE / '4c-admm-pbe' / f'Si{n}'
        dest = HERE / 'cases' / f'Si{n}'
        dest.mkdir(parents=True, exist_ok=False)
        source_input = original / 'cp2k.inp'
        old_text = source_input.read_text()
        assert 'SCREEN_ON_INITIAL_P TRUE' in old_text
        assert 'MAX_MEMORY 12000' in old_text
        text, count = re.subn(r'(?m)^(\s*EPS_SCHWARZ\s+)1\.0E-6\s*$',
                             r'\g<1>1.0E-8', old_text)
        assert count == 1
        old_project = re.search(r'(?m)^\s*PROJECT\s+(\S+)', old_text).group(1)
        project = f'Si{n}-HSE06-4c-ADMM-fromPBE-e8-20261019'
        text, count = re.subn(r'(?m)^(\s*PROJECT\s+)\S+',
                             lambda m: m.group(1) + project, text)
        assert count == 1
        # The two replacements above are the only changes to the source input.
        restored = text.replace(project, old_project).replace('EPS_SCHWARZ 1.0E-8',
                                                               'EPS_SCHWARZ 1.0E-6')
        assert restored == old_text
        (dest / 'cp2k.inp').write_text(text)
        wfn_name = f'Si{n}-PBE-RESTART.wfn'
        source_wfn = original / wfn_name
        assert source_wfn.stat().st_size > 0
        shutil.copy2(source_wfn, dest / wfn_name)
        assert sha256(source_wfn) == sha256(dest / wfn_name)
        pbe_log = original / 'pbe.log'
        pbe_text = pbe_log.read_text()
        assert 'SCF run converged' in pbe_text and 'PROGRAM ENDED' in pbe_text
        timings = re.findall(r'^\s*CP2K\s+1\s+.*$', pbe_text, re.MULTILINE)
        pbe_seconds = float(timings[-1].split()[-1])
        ref = next(r for r in old_results if r['variant'] == '4c-admm'
                   and int(r['size']) == n)
        case = {'atoms': n, 'path': str(dest), 'project': project,
                'source_input': str(source_input), 'source_input_sha256': sha256(source_input),
                'input_sha256': sha256(dest / 'cp2k.inp'),
                'source_wfn': str(source_wfn), 'wfn_sha256': sha256(source_wfn),
                'source_pbe_log': str(pbe_log), 'source_pbe_log_sha256': sha256(pbe_log),
                'historical_pbe_seconds': pbe_seconds,
                'reference_atomic_admm_energy_Ha': float(ref['energy'])}
        cases.append(case)
        script = f'''#!/bin/bash
#SBATCH --job-name=cp2k-e8-Si{n}
#SBATCH --partition=cpu32
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --exclusive
#SBATCH --time=02:00:00
#SBATCH --chdir={dest}
#SBATCH --output={dest}/slurm-%j.out
#SBATCH --error={dest}/slurm-%j.err

exec bash "{HERE / 'run_case.sh'}" "{dest}"
'''
        (HERE / f'submit_Si{n}.slurm').write_text(script)
    manifest = {'purpose': 'Missing small-cell EPS_SCHWARZ=1e-8 CP2K benchmark points',
                'cp2k_module': 'cp2k-2024.3/oneapi-2024.2.1',
                'partition': 'cpu32', 'mpi_ranks': 32, 'omp_threads_per_rank': 1,
                'eps_schwarz': 1e-8, 'screen_on_initial_p': True,
                'admm': 'ADMMS/cpFIT3', 'max_memory_MiB_per_rank': 12000,
                'timing_protocol': 'Run HSE06 only from the existing PBE WFN; add the recorded historical PBE time, as for the Si128/256 e8 runs.',
                'cases': cases}
    (HERE / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    for case in cases:
        print(f"Si{case['atoms']}: prepared; existing PBE stage {case['historical_pbe_seconds']:.3f} s")


if __name__ == '__main__':
    main()
