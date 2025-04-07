#BSUB -J content
#BSUB -q hpc
#BSUB -W 120                    # Walltime limit (10 minute)
#BSUB -n 16
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=2GB]"  # Memory requirement
#BSUB -R"select[model==XeonGold6226R]"
#BSUB -o content_%J.out
#BSUB -e content_%J.err


# Run the script for different sizes
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

#time python parallel.py 100 4
#time python Assignment_5_1st.py 100 1
#time python Assignment_5_1st.py 100 2
#time python Assignment_5_1st.py 100 4
#time python Assignment_5_1st.py 100 8
#time python Assignment_5_1st.py 100 16


time python Assignment_5_2nd.py 100 1
time python Assignment_5_2nd.py 100 2
time python Assignment_5_2nd.py 100 4
time python Assignment_5_2nd.py 100 8
time python Assignment_5_2nd.py 100 16