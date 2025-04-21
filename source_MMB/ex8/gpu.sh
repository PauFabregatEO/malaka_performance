#!/bin/sh
#BSUB -q c02613
#BSUB -J cuda7000_100images
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=512MB]"
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -W 3:00
#BSUB -o output/cuda7000_%J.out
#BSUB -e output/cuda7000_%J.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

time python "gpu_cuda.py" 20