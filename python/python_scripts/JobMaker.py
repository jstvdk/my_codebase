import os

start = 0
stop = 20

for i in range(start,stop):
    job_file = open(f"/fefs/aswg/workspace/vadym.voitsekhovskyi/4LST/jobs/dl1_muon_analysis_run{i}.job", "w")

    job_file.writelines("#!/bin/bash\n")
    job_file.writelines("#BATCH --partition=short\n")
    job_file.writelines("#SBATCH --time=1:59:00\n")
    job_file.writelines("#SBATCH --ntasks=1\n")
    job_file.writelines("#SBATCH --mem-per-cpu=7000 # in MB\n")
    job_file.writelines(f"#SBATCH --output=/fefs/aswg/workspace/vadym.voitsekhovskyi/4LST/log/dl1_muon_analysis_run{i}.log\n")
    job_file.writelines(f"#SBATCH --error=/fefs/aswg/workspace/vadym.voitsekhovskyi/4LST/error/dl1_muon_analysis_run{i}.err\n")
    job_file.writelines("\n")
    job_file.writelines("eval \"$(conda shell.bash hook)\"\n")
    job_file.writelines("conda activate ctapipe\n")
    job_file.writelines("\n")
    job_file.writelines(f"srun 4LST_cleaning_cluster.py {i * 20} {i*20 + 20} \n")
    job_file.close()

for i in range(start,stop):
    command = f"sbatch /fefs/aswg/workspace/vadym.voitsekhovskyi/4LST/jobs/dl1_muon_analysis_run{i}.job"
    os.system(command)
    print(f"Sbatch number {i} runned")