#BSUB -J content
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -q hpc
#BSUB -W 120                    # Walltime limit (10 minute)
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=2GB]"  # Memory requirement
#BSUB -o content_%J.out
#BSUB -e content_%J.err


# Run the script for different sizes
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

#python -m cProfile -s time Assignment_10.py 10
nsys profile -o M python  Assignment_10.py 10
nsys stats M.nsys-rep
