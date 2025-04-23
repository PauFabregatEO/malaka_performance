#!/bin/sh
#BSUB -q gpuv100
#BSUB -J cuda7000_all_images
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=8GB]"
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -R "select[gpu32gb]"
#BSUB -W 3:00
#BSUB -o output/cuda7000_all_im_%J.out
#BSUB -e output/cuda7000_all_im_%J.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

time python "gpu_cuda.py" 4571