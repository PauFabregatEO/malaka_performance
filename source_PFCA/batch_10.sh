#!/bin/bash
#BSUB -J HPC_mini_project_v0_pfca
#BSUB -q c02613
#BSUB -o batch_output_out_A10/Output_%J.out
#BSUB -e batch_output_err_A10/Output_%J.err
#BSUB -W 01:00
#BSUB -n 4
#BUSB -gpu "num=1:mode=exclusive_process"
#BSUB -R "rusage[mem=1GB]"
#BSUB -R "span[hosts=1]"
#BSUB -R "select[model == XeonGold6226R]"
# -- end of LSF options -- 

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

nsys profile -o output_profiler_9 python Assignment_9.py 20
nsys stats output_profiler_9.nsys-rep