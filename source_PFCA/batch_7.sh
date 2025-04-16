#!/bin/bash
#BSUB -J HPC_mini_project_v0_pfca
#BSUB -q hpc
#BSUB -o batch_output_out_A7/Output_%J.out
#BSUB -e batch_output_err_A7/Output_%J.err
#BSUB -W 01:00
#BSUB -n 8
#BSUB -R "rusage[mem=1GB]"
#BSUB -R "span[hosts=1]"
#BSUB -R "select[model == XeonGold6226R]"
# -- end of LSF options -- 

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

time python Assignment_7.py 100
#time python Assignment_7_paral.py 100