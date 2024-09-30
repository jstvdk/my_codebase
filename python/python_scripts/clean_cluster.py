import os


start = 1
stop = 2


for i in range(start,stop):
    subrun = eval(str(4-len(str(i))))*'0' + str(i)
    job_file = open(f"/fefs/aswg/workspace/vadym.voitsekhovskyi/1LST/jobs/r0_to_dl_data_run{i}.job", "w")


    job_file.writelines("#!/bin/bash\n")
    job_file.writelines("#BATCH --partition=short\n")
    job_file.writelines("#SBATCH --time=1:59:00\n")
    job_file.writelines("#SBATCH --ntasks=1\n")
    job_file.writelines("#SBATCH --mem-per-cpu=7000 # in MB\n")
    job_file.writelines(f"#SBATCH --output=/fefs/aswg/workspace/vadym.voitsekhovskyi/1LST/log/r0_to_dl1_data_run{i}_flag.log\n")
    job_file.writelines(f"#SBATCH --error=/fefs/aswg/workspace/vadym.voitsekhovskyi/1LST/error/r0_to_dl1_data_run{i}_flag.err\n")
    job_file.writelines("\n")
    job_file.writelines("eval \"$(conda shell.bash hook)\"\n")
    job_file.writelines("conda activate lstchain\n")
    job_file.writelines("\n")
    job_file.writelines(f"srun /home/vadym.voitsekhovskyi/mambaforge/envs/lstchain/lib/python3.11/site-packages/lstchain/scripts/lstchain_data_r0_to_dl1_flag.py --input-file /fefs/aswg/data/real/R0/20231007/LST-1.1.Run14948.{subrun}.fits.fz --output-dir /fefs/aswg/workspace/vadym.voitsekhovskyi/1LST/output_flag50 --pedestal-file /fefs/aswg/data/real/monitoring/PixelCalibration/Cat-A/drs4_baseline/20231007/v0.10.2/drs4_pedestal.Run14937.0000.h5 --calibration-file /fefs/aswg/data/real/monitoring/PixelCalibration/Cat-A/calibration/20231007/v0.10.4/calibration_filters_52.Run14938.0000.h5 --time-calibration-file /fefs/aswg/data/real/monitoring/PixelCalibration/Cat-A/drs4_time_sampling_from_FF/20220518/v0.10.0/time_calibration.Run08349.0000.h5 --pointing-file /fefs/onsite/monitoring/driveLST1/DrivePositioning/DrivePosition_log_20231007.txt --systematic-correction-file=/fefs/aswg/data/real/monitoring/PixelCalibration/Cat-A/ffactor_systematics/20230410/v0.10.3/calibration_scan_fit_20230410.0000.h5 --config=/fefs/aswg/lstosa/config_files_lstchain/lstchain_standard_v0.10_heuristic_ff.json \n")
    job_file.close()

for i in range(start,stop):
    command = f"sbatch /fefs/aswg/workspace/vadym.voitsekhovskyi/1LST/jobs/r0_to_dl_data_run{i}.job"
    os.system(command)
    print(f"Sbatch number {i} runned")