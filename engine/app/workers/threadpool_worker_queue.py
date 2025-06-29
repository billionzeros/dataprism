import queue
import threading

class ThreadPoolWorkerQueue:
    """
    A thread-safe worker queue for handling I/O-bound tasks.

    This class creates a pool of worker threads that continuously pull tasks 
    from a queue and execute them.
    """
    def __init__(self, num_workers=10):
        """
        Initializes the worker queue.

        Args:
            num_workers (int): The number of concurrent worker threads to run.
        """
        self.num_workers = num_workers
        self.task_queue = queue.Queue()
        self._workers = []
        self._start_workers()

    def _worker_loop(self):
        """The main loop for each worker thread."""
        while True:
            try:
                # The 'get()' call will block until a task is available.
                task = self.task_queue.get()

                # A 'None' task is a sentinel value to signal the worker to exit.
                if task is None:
                    break

                # Unpack the task, which is a tuple of (function, args, kwargs)
                func, args, kwargs = task
                
                # Execute the task
                func(*args, **kwargs)

            except Exception as e:
                # It's good practice to log errors but not kill the worker.
                print(f"Error in worker thread: {e}")
            finally:
                # Mark the task as done, important for the shutdown method.
                self.task_queue.task_done()
    
    def _start_workers(self):
        """Creates and starts the worker threads."""
        for _ in range(self.num_workers):
            thread = threading.Thread(target=self._worker_loop)
            thread.daemon = True  # Allows main program to exit even if workers are blocked
            thread.start()
            self._workers.append(thread)
            
    def add_task(self, func, *args, **kwargs):
        """
        Adds a task to the queue to be executed by a worker.

        Args:
            func: The function to execute.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.
        """
        task = (func, args, kwargs)
        self.task_queue.put(task)

    def shutdown(self, wait=True):
        """
        Shuts down the worker pool gracefully.

        Args:
            wait (bool): If True, waits for all queued tasks to complete 
            before shutting down.
        """
        if wait:
            # This blocks until all tasks in the queue are processed.
            self.task_queue.join()

        # Send a sentinel value (None) for each worker to signal them to exit.
        for _ in range(self.num_workers):
            self.task_queue.put(None)

        # Wait for all worker threads to terminate.
        for worker in self._workers:
            worker.join()
        
        print("All worker threads have been shut down.")
