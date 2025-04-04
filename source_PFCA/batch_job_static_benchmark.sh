#!/bin/bash
#BSUB -J HPC_mini_project_v0_pfca
#BSUB -q hpc
#BSUB -o batch_output_out/Output_%J.out
#BSUB -e batch_output_err/Output_%J.err
#BSUB -W 3:00
#BSUB -n 20
#BSUB -R "rusage[mem=512MB]"
#BSUB -R "span[hosts=1]"
#BSUB -R "select[model == XeonGold6226R]"
# -- end of LSF options -- 

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

#kernprof -l simulate.py
time simulate.py 32
time simulate_static_scheduling.py 32 1
time simulate_static_scheduling.py 32 2
time simulate_static_scheduling.py 32 4
time simulate_static_scheduling.py 32 8
time simulate_static_scheduling.py 32 16
time simulate_static_scheduling.py 32 20