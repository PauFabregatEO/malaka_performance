#!/bin/bash
#BSUB -J dev10
#BSUB -q hpc
#BSUB -W 1:00
#BSUB -n 1
#BSUB -R "rusage[mem=10GB]"
#BSUB -o checkN10c_%J.out
#BSUB -e checkN10c_%J.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

python "deviations.py" 10