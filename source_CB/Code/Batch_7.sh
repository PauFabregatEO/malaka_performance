#BSUB -J content
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

time python Assignment_7_1st.py 100
#faster after running once Jit
time python Assignment_7_1st.py 100