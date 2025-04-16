#!/bin/bash
#BSUB -J HPC_mini_project_v0_pfca
#BSUB -q hpc
#BSUB -o batch_output_out/Output_%J.out
#BSUB -e batch_output_err/Output_%J.err
#BSUB -W 3:00
#BSUB -n 12
#BSUB -R "rusage[mem=512MB]"
#BSUB -R "span[hosts=1]"
#BSUB -R "select[model == XeonGold6226R]"
# -- end of LSF options -- 

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

#kernprof -l simulate.py
time Dynamic_starmap.py 300 8 38
time Dynamic_starmap.py 300 8 32
time Dynamic_starmap.py 300 8 28
time Dynamic_starmap.py 300 8 24
time Dynamic_starmap.py 300 8 20
time Dynamic_starmap.py 300 8 16 
time Dynamic_starmap.py 300 8 12
time Dynamic_starmap.py 300 8 8
time Dynamic_starmap.py 300 8 4
time Dynamic_starmap.py 300 8 2

#time Dynamic_starmap.py 100 16 7 
#time Dynamic_starmap.py 100 16 6 
#time Dynamic_starmap.py 100 16 5
#time Dynamic_starmap.py 100 16 4 
#time Dynamic_starmap.py 100 16 3
#time Dynamic_starmap.py 100 16 2
#time Dynamic_starmap.py 100 16 1 


