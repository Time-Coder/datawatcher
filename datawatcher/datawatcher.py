import threading
import time
from queue import SimpleQueue
import traceback
from dataclasses import dataclass, field
from typing import Callable, Any, List, Dict, Optional


@dataclass
class Task:
    func: Callable[[], Any]
    callback: Optional[Callable[[Any], Any]] = None
    history: List[Any] = field(default_factory=list)

    def clear(self):
        self.history.clear()

    def next(self):
        try:
            result = self.func()
            self.history.append(result)
            if self.callback is not None:
                self.callback(result)
        except BaseException as e:
            traceback.print_exc()
            self.history.append(None)


class DataWatcher:
    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        self._time_list: List[float] = []
        
        self._running: bool = False
        self._interval: float = 1.0
        self._thread: Optional[threading.Thread] = None
        self._cmd_queue: SimpleQueue = SimpleQueue()
        self._lock: threading.Lock = threading.Lock()

    def watch(self, func: Callable, key: str, callback: Optional[Callable] = None):
        if not callable(func):
            raise TypeError("func must be a callable")
        
        if callback is not None and not callable(callback):
            raise TypeError("callback must be a callable")
        
        with self._lock:
            self._tasks[key] = Task(func, callback)
            if self._running:
                self._tasks[key].history = [None] * len(self._time_list)

    def unwatch(self, key: str):
        with self._lock:
            if key in self._tasks:
                del self._tasks[key]

    def clear(self):
        with self._lock:
            self._tasks.clear()
            self._time_list.clear()

    def _run_loop(self):
        while True:
            cmd = self._cmd_queue.get()
            if not cmd:
                break

            start_time = None
            while self._running:
                with self._lock:
                    current_time = time.perf_counter()
                    if start_time is None:
                        start_time = current_time

                    self._time_list.append(current_time - start_time)
                    for task in self._tasks.values():
                        task.next()
                        
                time.sleep(self._interval)

    def start(self, interval: float = 1.0):
        if self._running:
            return
        
        self._running = True
        self._interval = interval
        if self._thread is None:
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()

        self._time_list.clear()
        for task in self._tasks.values():
            task.clear()

        self._cmd_queue.put(True)

    def stop(self):
        self._running = False
        
    def time_list(self) -> List[float]:
        with self._lock:
            return self._time_list
        
    def value_list(self, key: str) -> List[Any]:
        with self._lock:
            return self._tasks[key].history

    def __getitem__(self, key: str) -> List[Any]:
        return self.value_list(key)