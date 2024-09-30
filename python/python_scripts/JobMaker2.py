import os

start = 0
stop = 94

for i in range(start,stop):
    job_file = open(f"/fefs/aswg/workspace/vadym.voitsekhovskyi/1LST/jobs/raw{i}_1LST.job", "w")

    job_file.writelines("#!/bin/bash\n")
    job_file.writelines("#BATCH --partition=short\n")
    job_file.writelines("#SBATCH --time=1:59:00\n")
    job_file.writelines("#SBATCH --ntasks=1\n")
    job_file.writelines("#SBATCH --mem-per-cpu=7000 # in MB\n")
    job_file.writelines(f"#SBATCH --output=/fefs/aswg/workspace/vadym.voitsekhovskyi/1LST/log/1LST_raw_run{i}.log\n")
    job_file.writelines(f"#SBATCH --error=/fefs/aswg/workspace/vadym.voitsekhovskyi/1LST/error/1LST_raw_run{i}.err\n")
    job_file.writelines("\n")
    job_file.writelines("eval \"$(conda shell.bash hook)\"\n")
    job_file.writelines("conda activate ctapipe\n")
    job_file.writelines("\n")
    job_file.writelines(f"srun /fefs/aswg/workspace/vadym.voitsekhovskyi/1LST/code/1LST_rawFit.py {i} {i+1} \n")
    job_file.close()

for i in range(start,stop):
    command = f"sbatch /fefs/aswg/workspace/vadym.voitsekhovskyi/1LST/jobs/raw{i}_1LST.job"
    os.system(command)
    print(f"Sbatch number {i} runned")
