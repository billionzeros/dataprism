import multiprocessing
import os

# This function must be defined at the top level of the module to be picklable.
def example_cpu_task(number, task_name):
    """A sample function that simulates a CPU-bound task."""
    pid = os.getpid()
    print(f"[PID:{pid}] Starting CPU task: {task_name}")
    # Perform a computation-heavy loop
    result = sum(i * i for i in range(number))
    print(f"[PID:{pid}] Finished CPU task: {task_name} (Result starts with {str(result)[:10]}...)")


class MultiProcessWorkerQueue:
    """
    A process-safe worker queue for handling CPU-bound tasks.

    This class creates a pool of worker processes that continuously pull tasks
    from a queue and execute them in parallel.
    """
    def __init__(self, num_workers=None):
        """
        Initializes the worker queue.

        Args:
            num_workers (int, optional): The number of concurrent worker processes.
                                         Defaults to the number of CPU cores.
        """
        if num_workers is None:
            num_workers = multiprocessing.cpu_count()
            
        self.num_workers = num_workers
        self.task_queue = multiprocessing.JoinableQueue()
        self._workers = []
        self._start_workers()

    def _worker_loop(self):
        """The main loop for each worker process."""
        while True:
            try:
                task = self.task_queue.get()
                if task is None:
                    break
                
                func, args, kwargs = task
                func(*args, **kwargs)

            except Exception as e:
                print(f"Error in worker process: {e}")
            finally:
                self.task_queue.task_done()
    
    def _start_workers(self):
        """Creates and starts the worker processes."""
        for _ in range(self.num_workers):
            process = multiprocessing.Process(target=self._worker_loop)
            process.daemon = True
            process.start()
            self._workers.append(process)
            
    def add_task(self, func, *args, **kwargs):
        """
        Adds a task to the queue to be executed by a worker process.

        Args:
            func: The picklable function to execute.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.
        """
        task = (func, args, kwargs)
        self.task_queue.put(task)

    def shutdown(self, wait=True):
        """Shuts down the worker pool gracefully."""
        if wait:
            self.task_queue.join()

        for _ in range(self.num_workers):
            self.task_queue.put(None)

        for worker in self._workers:
            worker.join()
        
        print("All worker processes have been shut down.")