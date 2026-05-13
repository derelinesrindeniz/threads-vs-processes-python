import time
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


IO_TASK_COUNT = 50
WORKER_COUNT = 5
IO_DELAY = 0.1

CPU_WORKLOADS = [
    100_000,
    300_000,
    500_000,
    1_000_000,
    3_000_000,
    5_000_000,
    10_000_000,
    20_000_000
]


# This function measures how long another function takes to run.
def measure_time(function, *args):
    start = time.perf_counter()
    result = function(*args)
    finish = time.perf_counter()

    elapsed_time = finish - start
    return elapsed_time, result


# This function simulates an I/O-bound task by waiting for a short time.
def simulated_io_work():
    time.sleep(IO_DELAY)


# This function runs all I/O tasks one by one.
def run_sequential_io():
    finished_tasks = 0

    for _ in range(IO_TASK_COUNT):
        simulated_io_work()
        finished_tasks += 1

    return finished_tasks


# This function runs the I/O tasks using 5 threads.
def run_threaded_io():
    finished_tasks = 0
    counter_lock = threading.Lock()

    # This inner function is the job that each thread runs.
    def thread_job():
        nonlocal finished_tasks

        simulated_io_work()

        with counter_lock:
            finished_tasks += 1

    with ThreadPoolExecutor(max_workers=WORKER_COUNT) as executor:
        jobs = [executor.submit(thread_job) for _ in range(IO_TASK_COUNT)]

        for job in jobs:
            job.result()

    return finished_tasks


# This function is the job that each process runs in the I/O test.
def process_io_job(shared_counter, shared_lock):
    time.sleep(IO_DELAY)

    with shared_lock:
        shared_counter.value += 1


# This function runs the I/O tasks using 5 processes.
def run_process_io():
    shared_counter = multiprocessing.Value("i", 0)
    shared_lock = multiprocessing.Lock()

    active_processes = []

    for _ in range(IO_TASK_COUNT):
        process = multiprocessing.Process(
            target=process_io_job,
            args=(shared_counter, shared_lock)
        )

        active_processes.append(process)
        process.start()

        # Keep only 5 processes active at the same time.
        if len(active_processes) == WORKER_COUNT:
            for p in active_processes:
                p.join()

            active_processes.clear()

    # Wait for any remaining processes to finish.
    for p in active_processes:
        p.join()

    return shared_counter.value


# This function does a CPU-heavy calculation.
def calculate_sum_of_squares(limit):
    result = 0

    for number in range(limit):
        result += number * number

    return result


# This function runs the CPU-bound task using 5 threads.
def run_cpu_test_with_threads(workload_size):
    with ThreadPoolExecutor(max_workers=WORKER_COUNT) as executor:
        jobs = [
            executor.submit(calculate_sum_of_squares, workload_size)
            for _ in range(WORKER_COUNT)
        ]

        for job in jobs:
            job.result()


# This function runs the CPU-bound task using 5 processes.
def run_cpu_test_with_processes(workload_size):
    with ProcessPoolExecutor(max_workers=WORKER_COUNT) as executor:
        jobs = [
            executor.submit(calculate_sum_of_squares, workload_size)
            for _ in range(WORKER_COUNT)
        ]

        for job in jobs:
            job.result()


# This function runs the I/O experiment and prints the results.
def print_io_results():
    print("=== Scenario 1: I/O-bound Simulation ===")
    print(f"Total tasks: {IO_TASK_COUNT}")
    print(f"Workers used for parallel versions: {WORKER_COUNT}")
    print()

    sequential_time, sequential_done = measure_time(run_sequential_io)
    threading_time, threading_done = measure_time(run_threaded_io)
    process_time, process_done = measure_time(run_process_io)

    print("Method             | Time (seconds) | Completed Tasks")
    print("-------------------|----------------|----------------")
    print(f"Sequential         | {sequential_time:<14.4f} | {sequential_done}")
    print(f"Threading          | {threading_time:<14.4f} | {threading_done}")
    print(f"Multiprocessing    | {process_time:<14.4f} | {process_done}")

    return {
        "sequential": sequential_time,
        "threading": threading_time,
        "multiprocessing": process_time
    }


# This function runs the CPU experiment and finds the break-even point.
def print_cpu_results():
    print()
    print("=== Scenario 2: CPU-bound Break-even Test ===")
    print(f"Workers used: {WORKER_COUNT}")
    print()

    print("Workload Size | Threading Time | Multiprocessing Time")
    print("--------------|----------------|---------------------")

    first_process_win = None

    for workload in CPU_WORKLOADS:
        threading_time, _ = measure_time(run_cpu_test_with_threads, workload)
        process_time, _ = measure_time(run_cpu_test_with_processes, workload)

        print(f"{workload:<13} | {threading_time:<14.4f} | {process_time:.4f}")

        if first_process_win is None and process_time < threading_time:
            first_process_win = workload

    print()

    if first_process_win is None:
        print("Break-even point was not found in the tested workload range.")
    else:
        print(f"Approximate break-even point: workload size = {first_process_win}")

    return first_process_win


# This function starts both experiments.
def main():
    print_io_results()
    print_cpu_results()


# This part starts the program safely on Windows.
if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()