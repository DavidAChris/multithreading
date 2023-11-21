import os
import queue
import threading


class Worker(threading.Thread):
    def __init__(self, task_queue, result_queue):
        super().__init__()
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args = self.task_queue.get()
            if func is None:
                break
            try:
                result = func(*args)
            except Exception as err:
                result = err
            self.result_queue.put(result)
            self.task_queue.task_done()


class ThreadPool:
    def __init__(self, threads=os.cpu_count() or 1):
        self.num_threads = threads
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.workers = []

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def start(self):
        self.workers = [Worker(self.task_queue, self.result_queue) for _ in range(self.num_threads)]

    def map_async(self, func, iterable):
        for args in iterable:
            self.task_queue.put((func, (args,)))
        self.task_queue.join()
        results = Results([self.result_queue.get() for _ in iterable])
        return results

    def close(self):
        for _ in self.workers:
            self.task_queue.put((None, None))
        for worker in self.workers:
            worker.join()


class Results(list):
    def get(self):
        for result in self:
            if isinstance(result, Exception):
                raise result
