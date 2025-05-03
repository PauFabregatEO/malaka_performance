#!/bin/sh
#BSUB -q c02613
#BSUB -J cuda20000_100_im
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=16GB]"
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -W 1:00
#BSUB -o output/cuda20000_100_im_%J.out
#BSUB -e output/cuda20000_100_im_%J.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

time python "gpu_cuda.py" 100