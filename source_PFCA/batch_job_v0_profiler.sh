#!/bin/bash
#BSUB -J HPC_mini_project_v0_pfca
#BSUB -q hpc
#BSUB -o Output_%J.out
#BSUB -e Output_%J.err
#BSUB -W 00:10
#BSUB -n 4
#BSUB -R "rusage[mem=2GB]"
#BSUB -R "span[hosts=1]"
#BSUB -R "select[model == XeonGold6226R]"
# -- end of LSF options -- 

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

python -m line_profiler -rmt "simulate.py.lprof"