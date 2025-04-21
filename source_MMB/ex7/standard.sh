#!/bin/bash
#BSUB -J standard
#BSUB -q hpc
#BSUB -W 3:00
#BSUB -n 1
#BSUB -R "rusage[mem=10GB]"
#BSUB -R "select[model == XeonGold6226R]"
#BSUB -o output/standard_%J.out
#BSUB -e output/standard_%J.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

time python standard.py 100