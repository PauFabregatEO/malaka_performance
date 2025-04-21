#!/bin/bash
#BSUB -J jit
#BSUB -q hpc
#BSUB -W 3:00
#BSUB -n 1
#BSUB -R "rusage[mem=1GB]"
#BSUB -R "select[model == XeonGold6226R]"
#BSUB -o output/jit_image_%J.out
#BSUB -e output/jit_image_%J.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

time python jit_implementation.py 1