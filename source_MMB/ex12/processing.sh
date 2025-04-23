#!/bin/bash
#BSUB -J processing
#BSUB -q hpc
#BSUB -W 0:30
#BSUB -n 1
#BSUB -R "rusage[mem=1GB]"
#BSUB -o output/processing_%J.out
#BSUB -e output/processing_%J.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

python "processing.py"