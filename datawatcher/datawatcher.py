import threading
import time
from collections import defaultdict
from queue import SimpleQueue
import traceback
from typing import Callable, Any, List, Dict, Optional


class DataWatcher:
    def __init__(self):
        self._tasks: Dict[str, Callable] = {}
        self._history: Dict[str, List[Any]] = defaultdict(list)
        self._time_list: List[float] = []
        
        self._running = False
        self._interval: float = 1.0
        self._thread: Optional[threading.Thread] = None
        self._cmd_queue: SimpleQueue = SimpleQueue()
        self._lock: threading.Lock = threading.Lock()

    def watch(self, func: Callable, key: str):
        if not callable(func):
            raise TypeError("func must be a callable")
        
        with self._lock:
            self._tasks[key] = func

    def unwatch(self, key: str):
        with self._lock:
            if key in self._tasks:
                del self._tasks[key]
                del self._history[key]

    def clear(self):
        with self._lock:
            self._tasks.clear()
            self._history.clear()

    def _run_loop(self):
        while True:
            cmd = self._cmd_queue.get()
            if not cmd:
                break

            start_time = time.perf_counter()
            while self._running:
                with self._lock:
                    current_time = time.perf_counter()
                    self._time_list.append(current_time - start_time)
                    for key, func in self._tasks.items():
                        if not self._running:
                            break

                        try:
                            result = func()
                            self._history[key].append(result)
                        except BaseException as e:
                            traceback.print_exc()
                            self._history[key].append(None)
                        
                time.sleep(self._interval)

    def start(self, interval: float = 1.0):
        if self._running:
            return
        
        self._running = True
        self._interval = interval
        if self._thread is None:
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()

        self._cmd_queue.put(True)

    def stop(self):
        self._running = False
        
    def time_list(self)->List[float]:
        with self._lock:
            return list(self._time_list)
        
    def value_list(self, key: str)->List[Any]:
        with self._lock:
            return list(self._history[key])

    def __getitem__(self, key: str) -> List[Any]:
        return self.value_list(key)