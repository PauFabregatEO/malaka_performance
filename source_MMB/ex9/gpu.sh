#!/bin/sh
#BSUB -q c02613
#BSUB -J cupy7000_100images
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=512MB]"
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -W 3:00
#BSUB -o output/cupy7000_100im_%J.out
#BSUB -e output/cupy7000_100im_%J.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

time python "gpu_cupy.py" 100