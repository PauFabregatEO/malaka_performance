#!/bin/bash
#BSUB -J timing
#BSUB -q hpc
#BUSB -n 1
#BSUB -W 5
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=1GB]"
#BSUB -R "select[model == XeonE5_2650v4]"
#BSUB -o batch_output/time_jacobi_%J.out
#BSUB -e batch_output/time_jacobi_%J.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

kernprof -l "simulate.py" 1