#!/bin/bash
#BSUB -J timing
#BSUB -q hpc
#BSUB -W 3:00
#BSUB -n 20
#BSUB -R "rusage[mem=512MB]"
#BSUB -R "span[hosts=1]"
#BSUB -R "select[model == XeonGold6226R]"
#BSUB -o batch_output/dynamic_timing_%J.out
#BSUB -e batch_output/dynamic_timing_%J.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

python -u "simulate.py" 100