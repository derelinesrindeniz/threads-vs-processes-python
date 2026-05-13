# Threads vs Processes Performance Comparison

This project compares sequential execution, multithreading, and multiprocessing in Python.

The main goal of this project is to observe the performance differences between threads and processes for I/O-bound and CPU-bound tasks.

## Technologies Used

- Python
- threading
- multiprocessing
- concurrent.futures
- time.perf_counter

## Features

- Measures execution time of sequential execution
- Compares ThreadPoolExecutor and ProcessPoolExecutor
- Tests I/O-bound task performance
- Tests CPU-bound task performance
- Finds an approximate break-even point for multiprocessing performance

## What I Learned

Through this project, I practiced Python concurrency concepts such as threads, processes, execution time measurement, and performance comparison. I also learned how multithreading and multiprocessing behave differently depending on the task type.

## How to Run

```bash
python main.py
