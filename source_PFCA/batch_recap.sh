#!/bin/bash
#BSUB -J HPC_mini_project_v0_pfca
#BSUB -q hpc
#BSUB -o batch_output_out_recap/Output_%J.out
#BSUB -e batch_output_err_recap/Output_%J.err
#BSUB -W 03:00
#BSUB -n 8
#BSUB -R "rusage[mem=1GB]"
#BSUB -R "span[hosts=1]"
#BSUB -R "select[model == XeonGold6226R]"
# -- end of LSF options -- 

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

#time python simulate.py 20

#time python Try_v2.py 100 20
#time python Try_v2.py 100 16
#time python Try_v2.py 100 12
#time python Try_v2.py 100 8
#time python Try_v2.py 100 4
#time python Try_v2.py 100 2

time python Dynamic_starmap.py 100 8 13
time python Dynamic_starmap.py 100 8 10
time python Dynamic_starmap.py 100 8 8
time python Dynamic_starmap.py 100 8 6
time python Dynamic_starmap.py 100 8 4
time python Dynamic_starmap.py 100 8 2
time python Dynamic_starmap.py 100 8 1