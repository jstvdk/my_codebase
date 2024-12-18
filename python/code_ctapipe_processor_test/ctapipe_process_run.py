#!/usr/bin/env python

import argparse
import logging
import glob
import os
import subprocess as sp
import numpy as np
import re

def main():

    parser = argparse.ArgumentParser(
        description=("Script to process R0 to DL1 files using ctapipe"))
    parser.add_argument('--input_dir', '-i',
                        help='Input directory containing the FITS.FZ files',
                        default="./")
    parser.add_argument('--run', '-r',
                        type=int,
                        required=True,
                        help='Run number to process (integer)')
    parser.add_argument('--subrun_start', '-s_start',
                        type=int,
                        default=0,
                        help='Starting subrun number (integer, e.g., 0)')
    parser.add_argument('--subrun_stop', '-s_stop',
                        type=int,
                        required=True,
                        help='Ending subrun number (integer, inclusive, e.g., 200)')
    parser.add_argument('--config', '-c',
                        help='ctapipe config file',
                        default="/fefs/aswg/workspace/vadym.voitsekhovskyi/2024muons/lst_study/focal_length_comparison/data/16903_run_processor_tool_config.yaml")
    parser.add_argument('--output_dir', '-o',
                        help='Output directory',
                        default="./")

    args = parser.parse_args()

    # Set up logging to output to the console only
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Set the minimum log level to INFO

    # Create a formatter that specifies the log message format
    formatter = logging.Formatter('%(asctime)s %(levelname)s:%(message)s')

    # Create a StreamHandler to output logs to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Set log level for the console handler
    console_handler.setFormatter(formatter)  # Apply the formatter to the console handler
    
    # Add the console handler to the logger
    if not logger.handlers:
        logger.addHandler(console_handler)

    logging.info(f"Processing Run: {args.run}")
    logging.info(f"Subruns: {args.subrun_start} to {args.subrun_stop}")

    # Generate zero-padded subrun numbers using the user's approach
    subrun_list = []
    start = args.subrun_start
    stop = args.subrun_stop + 1  # To include the stop value

    for i in range(start, stop):
        padding = 4 - len(str(i))
        subrun = padding * '0' + str(i)
        subrun_list.append(subrun)

    logging.info(f"Generated Subrun List: {subrun_list}")

    # Input handling
    abs_file_dir = os.path.abspath(args.input_dir)
    # Construct pattern to match the specific run and any subrun
    pattern = os.path.join(abs_file_dir, f"LST-1.1.Run{args.run}.*.fits.fz")
    all_files = np.sort(glob.glob(pattern))

    logging.info(f"Found {len(all_files)} files to process.")

    for file in all_files:

        filename = os.path.basename(file)
        # Replace 'fits.fz' with 'dl1.h5' and adjust naming as needed
        output_file = os.path.join(args.output_dir, filename.replace('.fits.fz', 'dl1.h5'))
        print(f"Output file: '{output_file}'")
        logging.info(f"Processing file: {file} -> {output_file}")

        cmd = [
             "sbatch",
             "-A",
             "aswg",
             "--output=/fefs/aswg/workspace/vadym.voitsekhovskyi/2024muons/lst_study/focal_length_comparison/data/log/slurm_%A_%a.out",
             "ctapipe-process",
             "--overwrite",
             f"--input={file}",
             f"--output={output_file}",
             f"--config={args.config}",
             "--ProcessorTool.provenance_log=/fefs/aswg/workspace/vadym.voitsekhovskyi/2024muons/lst_study/focal_length_comparison/data/log/provenance_log.log",
            ]
        print(f"Submitting job with command: {' '.join(cmd)}")
        logging.info(f"Submitting job: {' '.join(cmd)}")
        try:
            sp.run(cmd, check=True)
            logging.info(f"Successfully submitted job for {file}")
        except sp.CalledProcessError as e:
            logging.error(f"Failed to submit job for {file}: {e}")
            print(f"Failed to submit job for {file}: {e}")

    return        

if __name__ == "__main__":
    main()