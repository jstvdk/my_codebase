import subprocess
import sys

def run_command(command, description):
    """
    Runs a shell command and handles errors.

    Parameters:
    - command (list): The command and its arguments as a list.
    - description (str): Description of the command for logging purposes.
    """
    try:
        print(f"Starting: {description}")
        # Execute the command
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(f"Completed: {description}\n")
        # Optionally, you can print the output
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error while executing: {description}")
        print(f"Return Code: {e.returncode}")
        print(f"Error Output:\n{e.stderr}")
        sys.exit(e.returncode)  # Exit the script with the same error code

def main():
    # Define the first command as a list of arguments
    command1 = [
        "python3",
        "/Users/vdk/Software/ctasoft/cta-lstchain/lstchain/scripts/lstchain_mc_r0_to_dl1.py",
        "--input-file",
        "/Users/vdk/muons2024/simtel_files/2024year_tuned_nooulier_reflectivity_additional/run101_muon.simtel.gz",
        "--output-dir",
        "/Users/vdk/Software/ctapipe_processor_test/lstchain_comparison",
        "--config",
        "/Users/vdk/Software/ctapipe_processor_test/lstchain_standard_config.json"
    ]

    # Define the second command as a list of arguments
    command2 = [
        "python3",
        "/Users/vdk/Software/ctasoft/cta-lstchain/lstchain/scripts/lstchain_dl1_muon_analysis.py",
        "--input-file",
        "/Users/vdk/Software/ctapipe_processor_test/lstchain_comparison/dl1_run101_muon.h5",
        "--output-file",
        "/Users/vdk/Software/ctapipe_processor_test/lstchain_comparison/muon_table.fits"
    ]

    # Execute the first command
    run_command(command1, "lstchain_mc_r0_to_dl1.py")

    # Execute the second command after the first one completes successfully
    run_command(command2, "lstchain_dl1_muon_analysis.py")

    print("Both commands executed successfully.")

if __name__ == "__main__":
    main()