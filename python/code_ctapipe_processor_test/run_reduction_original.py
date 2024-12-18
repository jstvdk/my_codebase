#!/usr/bin/env python

import argparse
import logging
import glob
import os
import subprocess as sp
import numpy as np


def main():

    parser = argparse.ArgumentParser(
        description=("Script to run reduction from simtel files to DL1 hdf5 files with the ctapipe-process tool"))
    parser.add_argument('--input_dir', '-i',
                        help='input directory',
                        default="./")
    parser.add_argument('--pattern', '-p',
                        help='pattern to mask unwanted files',
                        default="*.simtel.gz")
    parser.add_argument('--type',
                        help='particle type',
                        default="gamma")
    parser.add_argument('--config', '-c',
                        help='ctapipe config file',
                        default="/home/tjark.miener/config_files/ctapipe_standard_pmt_config.json")
    parser.add_argument('--output_dir', '-o',
                        help='output directory',
                        default="./")

    args = parser.parse_args()

    # Input handling
    abs_file_dir = os.path.abspath(args.input_dir)
    files = np.sort(glob.glob(os.path.join(abs_file_dir, args.pattern)))

    for file in files:
        print(f"Inputfile: '{file}'")
        #startnr_run = f"{file.split('/')[-1].replace('simtel_corsika_run', '')[0]}"
        #print(startnr_run)
        #if startnr_run != "7":
        #    print("skipping")
        #    continue
        output_file = f"{args.output_dir}/{file.split('/')[-1].replace('simtel_corsika', f'{args.type}').replace('simtel.gz', 'dl1.h5')}"
        print(f"Outputfile: '{output_file}'")
        cmd = [
             "sbatch",
             "-A",
             "aswg",
             "--output=/fefs/aswg/workspace/tjark.miener/dl1_pmt/slurm_%A_%a.out",
             f"ctapipe-process",
             #"-t 1",
             #"-v",
             "--overwrite",
             f"--input={file}",
             f"--output={output_file}",
             f"--config={args.config}",
             f"--DataWriter.write_dl1_images=True",
             f"--DataWriter.write_dl1_parameters=True",
             f"--DataWriter.write_dl2=True",
             #f"--DataWriter.write_raw_waveforms=True",
             #f"--DataWriter.write_r1_waveforms=True",
             "--ProcessorTool.provenance_log=/fefs/aswg/workspace/tjark.miener/dl1_pmt/provenance_log.log",
             f"--DataWriter.write_index_tables=True"
            ]
        print(cmd)
        sp.run(cmd)
    return        

if __name__ == "__main__":
    main()

