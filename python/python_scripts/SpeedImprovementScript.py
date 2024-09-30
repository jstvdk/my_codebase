from joblib import Parallel, delayed
import joblib
import time
import sys
import CleaningRings


if __name__ == "__main__":

    number_of_cpu = joblib.cpu_count()

    delayed_funcs = [delayed(CleaningRings.cleaning_rings_file)(i) for i in range(78,100)]
    parallel_pool = Parallel(n_jobs=number_of_cpu)
    start = time.time()
    parallel_pool(delayed_funcs)
    end = time.time()
    print(f'time of execution = {end - start}')

