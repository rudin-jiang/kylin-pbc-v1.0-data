#!/usr/bin/env python3
"""Rebuild the EPS_SCHWARZ=1e-8 summary from the archived CP2K/PBE logs.

Run from any working directory. No temporary benchmark tree is needed.
Keep this directory inside the complete kylin-pbc-v1.0-data archive because
historical e6 and Kylin comparison logs are read from sibling directories.
"""
import csv
import hashlib
import json
import math
from pathlib import Path
import re
from statistics import mean

HERE = Path(__file__).resolve().parent
SIZES = (16, 32, 64, 128, 256)
NUMBER = r'[-+0-9.Ee]+'


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract(text, pattern, cast=float):
    matches = re.findall(pattern, text, re.MULTILINE)
    if not matches:
        raise ValueError(f'Missing field: {pattern}')
    return cast(matches[-1])


def cp2k_log(path, hfx=True):
    text = path.read_text()
    assert 'PROGRAM ENDED' in text, path
    assert 'ABORT' not in text and 'KILLED BY SIGNAL' not in text, path
    assert 'SCF run converged' in text, path
    total = extract(text, r'^\s*CP2K\s+1\s+1\.0\s+\S+\s+\S+\s+\S+\s+(\S+)\s*$')
    energy = extract(text, r'ENERGY\| Total FORCE_EVAL \( QS \) energy \[a\.u\.\]:\s+(' + NUMBER + ')')
    if not hfx:
        return {'total_seconds': total, 'energy_Ha': energy}
    steps = re.findall(r'^\s*\d+\s+OT\s+(?:DIIS|SD|LS)\s+\S+\s+(' + NUMBER + r')\s+(' + NUMBER + r')\s+(' + NUMBER + r')\s+(' + NUMBER + r')\s*$', text, re.MULTILINE)
    assert steps, path
    outer = re.findall(r'outer SCF loop converged in\s+(\d+) iterations or\s+(\d+) steps', text)
    assert outer, path
    assert int(outer[-1][1]) == len(steps), path
    steps = [tuple(float(x) for x in step) for step in steps]
    assert steps[-1][1] <= 1e-6, path
    incore = extract(text, r"Number of sph. ERI's stored in-core:\s+(\d+)", int)
    onfly = extract(text, r"Number of sph. ERI's calculated on the fly:\s+(\d+)", int)
    return {
        'energy_Ha': energy,
        'hse_seconds': total,
        'hse_ot_steps': len(steps),
        'outer_scf_iterations': int(outer[-1][0]),
        'final_ot_gradient': steps[-1][1],
        'final_ot_energy_change_Ha': steps[-1][3],
        'first_hse_iteration_seconds': steps[0][0],
        'later_hse_iteration_mean_seconds': mean(s[0] for s in steps[1:]),
        'eri_total_GiB': extract(text, r"Total memory consumption ERI's RAM \[MiB\]:\s+(\d+)") / 1024,
        'peak_memory_per_rank_GiB': extract(text, r'max memory usage/rank\s+(' + NUMBER + ')') / 2**30,
        'cp2k_estimated_peak_process_MiB': extract(text, r'MEMORY\| Estimated peak process memory \[MiB\]\s+(\d+)', int),
        'eri_incore_count': incore,
        'eri_onfly_count': onfly,
        'eri_onfly_fraction': onfly / (incore + onfly),
        'eri_disk_count': extract(text, r"Number of sph. ERI's stored on disk:\s+(\d+)", int),
        'periodic_image_cells': extract(text, r'Number of periodic image cells considered:\s+(\d+)', int),
        'eps_schwarz': extract(text, r'HFX_INFO\| EPS_SCHWARZ:\s+(' + NUMBER + ')'),
        'effective_cutoff_angstrom': extract(text, r'HFX_INFO\| Cutoff Radius \[angstrom\]:\s+(' + NUMBER + ')'),
        'warning_count': extract(text, r'The number of warnings for this run is\s*:\s*(\d+)', int),
        'cutoff_exceeds_half_cell_warning': 'cutoff radius is larger than half the minimal cell dimension' in text,
        'mpi_ranks': extract(text, r'Total number of message passing processes\s+(\d+)', int),
        'omp_threads': extract(text, r'GLOBAL\| Number of threads for this process\s+(\d+)', int),
        'cpu_model': extract(text, r'GLOBAL\| CPU model name\s+(.+)', str).strip(),
        'node': extract(text, r'PROGRAM STARTED ON\s+(\S+)', str),
        'cp2k_version': extract(text, r'version string:\s+CP2K version\s+(\S+)', str),
        'cp2k_revision': extract(text, r'source code revision number:\s+(\S+)', str),
    }


def slope(xs, ys):
    x, y = [math.log(v) for v in xs], [math.log(v) for v in ys]
    xm, ym = mean(x), mean(y)
    return sum((a-xm)*(b-ym) for a,b in zip(x,y)) / sum((a-xm)**2 for a in x)


def main():
    provenance = json.loads((HERE / 'provenance.json').read_text())
    for entry in provenance['files']:
        assert sha256(HERE / entry['archive_path']) == entry['archive_sha256'], entry
    rows, source_hashes = [], {}
    for n in SIZES:
        case = HERE / f'Si{n}-HSE06'
        log, inp = case / 'cp2k.log', case / 'cp2k.inp'
        inp_text = inp.read_text()
        assert re.search(r'^\s*EPS_SCHWARZ\s+1\.0E-8\s*$', inp_text, re.MULTILINE)
        assert 'SCREEN_ON_INITIAL_P TRUE' in inp_text
        assert 'ADMMS' in inp_text and 'AUX_FIT cpFIT3' in inp_text
        hse = cp2k_log(log)
        assert hse['eps_schwarz'] == 1e-8
        assert hse['mpi_ranks'] == 32 and hse['omp_threads'] == 1
        assert hse['cp2k_version'] == '2024.3' and hse['cp2k_revision'] == 'git:6712648'
        pbe_log = case / 'pbe.log'
        pbe = cp2k_log(pbe_log, hfx=False)
        e6_log = HERE.parent / 'pbe-restart' / f'Si{n}-HSE06' / 'cp2k.log'
        e6 = cp2k_log(e6_log)
        atomic_log = HERE.parent / 'atomic-guess' / f'Si{n}-HSE06' / 'cp2k.log'
        atomic = cp2k_log(atomic_log)
        kylin_log = HERE.parents[2] / 'scaling' / f'Si{n}-HSE06' / 'kylin-pbc.log'
        kylin = round(extract(kylin_log.read_text(), r'Timer "Kylin-PBC main" used time: (' + NUMBER + ') s'), 3)
        if n <= 64:
            assert (case / 'job-evidence/exitcode.txt').read_text().strip() == '0'
            job_id = extract((case / 'job-evidence/run_metadata.txt').read_text(), r'^job_id=(\d+)$', str)
            evidence = f'Si{n}-HSE06/job-evidence/submit_Si{n}.slurm'
        else:
            job_id = '249374'
            evidence = 'job-evidence-large/submit_extra.slurm'
            completed = (HERE / 'job-evidence-large/slurm-249374.out').read_text()
            assert re.search(r'done\s+4c-admm-pbe-e8/Si' + str(n) + r'/cp2k.inp rc=0', completed)
        assert '#SBATCH --partition=cpu32' in (HERE / evidence).read_text()
        total = round(hse['hse_seconds'] + pbe['total_seconds'], 3)
        e6_total = round(e6['hse_seconds'] + pbe['total_seconds'], 3)
        row = {
            'atoms': n,
            'cp2k_total_including_pbe_seconds': total,
            'pbe_seconds_historical': pbe['total_seconds'],
            'kylin_paper_atomic_seconds': kylin,
            'cp2k_over_kylin_time_ratio': total / kylin,
            'cp2k_e6_restart_total_seconds': e6_total,
            'e8_over_e6_time_ratio': total / e6_total,
            'delta_e8_minus_e6_restart_uHa_per_atom': (hse['energy_Ha'] - e6['energy_Ha']) / n * 1e6,
            'delta_e8_minus_e6_atomic_uHa_per_atom': (hse['energy_Ha'] - atomic['energy_Ha']) / n * 1e6,
            'e6_restart_screen_on_initial_p': n != 16,
            'max_memory_MiB_per_rank': extract(inp_text, r'^\s*MAX_MEMORY\s+(\d+)', int),
            'screen_on_initial_p': True,
            'admm': 'ADMMS/cpFIT3',
            'partition': 'cpu32',
            'node_memory_nominal_GB': 512,
            'job_id': job_id,
            'source_job_submission': evidence,
            **hse,
        }
        sources = {
            'source_log': f'Si{n}-HSE06/cp2k.log',
            'source_input': f'Si{n}-HSE06/cp2k.inp',
            'source_pbe_log': f'Si{n}-HSE06/pbe.log',
            'source_pbe_input': f'Si{n}-HSE06/pbe.inp',
            'source_e6_restart_log': f'../pbe-restart/Si{n}-HSE06/cp2k.log',
            'source_e6_atomic_log': f'../atomic-guess/Si{n}-HSE06/cp2k.log',
            'source_kylin_log': f'../../../scaling/Si{n}-HSE06/kylin-pbc.log',
        }
        row.update(sources)
        rows.append(row)
        for relative in [*sources.values(), evidence]:
            source_hashes[relative] = sha256(HERE / relative)
    notes = [
        'All source_* paths and source_sha256 keys are relative to this directory. Original absolute source paths and byte-identical copy hashes are retained in provenance.json.',
        'Timing uses the CP2K timer TOTAL TIME / MAXIMUM and excludes shell launch overhead. Total time is HSE06 plus the historical PBE-stage time; PBE was not rerun for e8.',
        'Kylin timings are read from the archived original manuscript atomic-guess logs and rounded to 3 decimals, matching the figure.',
        'All five e8 runs use EPS_SCHWARZ=1e-8, SCREEN_ON_INITIAL_P TRUE and ADMMS/cpFIT3. Historical e6 Si16 comparison uses the stable unscreened restart.',
        'The five e8 HSE06 runs used cpu32, 32 MPI ranks x 1 OpenMP thread, Xeon Gold 6544Y / nominal 512 GB nodes. The Si256 Kylin/CP2K atomic-guess figure points used a 2 TB Xeon Gold 6548N node.',
        'Si256 e8 MAX_MEMORY is 8000 MiB/rank and about 28% of its ERIs are recomputed each iteration; the e6 comparison used 5000 MiB/rank.',
        'eri_total_GiB is ERI memory summed over all ranks. peak_memory_per_rank_GiB preserves the historical DBCSR max memory usage/rank (bytes) / 2**30 definition.',
        'cp2k_estimated_peak_process_MiB is the separate final MEMORY| Estimated peak process memory [MiB] value. Multiplying any per-process maximum by 32 is not a measured simultaneous whole-node peak.',
        'The time.txt maxrss_rank0_kib field measures the MPI launcher and is not a CP2K memory measurement.',
        'Energy differences are within-CP2K setup sensitivities, not errors against an exact converged reference; ADMM remains enabled.',
        'All five logs contain converged SCF and PROGRAM ENDED; small runs have saved exitcode=0 and large runs have rc=0 in the Slurm output. The accounting database was unavailable.',
        'The logs retain periodic-cutoff and non-square-MPI-rank warnings; normal completion does not remove these caveats.',
        'Five-point fitted exponents describe these observed timings only; Si256 integral recomputation and mixed hardware preclude interpreting them as intrinsic scaling.',
        'Large PBE WFN binaries are omitted. Regenerate them with the archived pbe.inp in a new run directory; do not overwrite archived raw outputs.',
    ]
    summary = {
        'sizes': list(SIZES),
        'all_five_normal_end_and_converged': True,
        'new_jobs_all_exit_zero': True,
        'timing_unit': 's',
        'energy_unit': 'Ha',
        'energy_difference_unit': 'microhartree/atom',
        'source_path_base': '.',
        'provenance_file': 'provenance.json',
        'notes': notes,
        'effective_time_exponents': {
            'cp2k_e8_total': slope(SIZES, [r['cp2k_total_including_pbe_seconds'] for r in rows]),
            'kylin_paper_atomic_total': slope(SIZES, [r['kylin_paper_atomic_seconds'] for r in rows]),
        },
        'source_sha256': source_hashes,
        'results': rows,
    }
    with (HERE / 'results_eps8.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (HERE / 'summary_eps8.json').write_text(json.dumps(summary, indent=2) + '\n')
    for row in rows:
        print(f"Si{row['atoms']:3}: HSE {row['hse_seconds']:.3f} + PBE {row['pbe_seconds_historical']:.3f} = {row['cp2k_total_including_pbe_seconds']:.3f} s; peak estimate {row['cp2k_estimated_peak_process_MiB']} MiB/process")
    print('Verified archived sources; rebuilt results_eps8.csv and summary_eps8.json.')


if __name__ == '__main__':
    main()
