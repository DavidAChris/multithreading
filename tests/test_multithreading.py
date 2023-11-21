import os
from multithreading.pool import ThreadPool


class TestFailure(Exception):
    """Raise in case a test fails"""


thread_count_error = TestFailure("Failed to assign correct thread count")
test_failed = TestFailure("Failed to generate a ValueError from results")


def example_task(task_id):
    if task_id == 2:
        raise ValueError("An example error occurred in Task 2")
    return f"Task {task_id} executed"


def test_thread_pool():
    thread_count = 10
    with ThreadPool(threads=thread_count) as pool:
        if pool.num_threads != thread_count:
            raise thread_count_error
        results = pool.map_async(example_task, range(5))
        print(results)
        try:
            results.get()
            raise test_failed
        except ValueError:
            assert True


def test_default_threads():
    with ThreadPool() as pool:
        if pool.num_threads != os.cpu_count():
            if pool.num_threads != 1:
                raise thread_count_error
        results = pool.map_async(example_task, range(5))
        print(results)
        try:
            results.get()
            raise test_failed
        except ValueError:
            assert True


def test_high_thread_count():
    thread_count = 1000
    with ThreadPool(threads=thread_count) as pool:
        if pool.num_threads != thread_count:
            raise thread_count_error
        results = pool.map_async(example_task, range(2000))
        print(results[:10])
        try:
            results.get()
            raise test_failed
        except ValueError:
            assert True
