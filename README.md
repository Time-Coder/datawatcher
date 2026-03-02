# DataWatcher

A lightweight Python library for monitoring data changes and recording them to lists.

## Features

- Monitor multiple data sources simultaneously
- Record data changes over time
- Thread-safe operations
- Simple and intuitive API
- Lightweight with zero dependencies

## Installation

```bash
pip install datawatcher
```

## Examples

### Quick Start

```python
from datawatcher import DataWatcher
import time

# Create a watcher instance
watcher = DataWatcher()

# Define a variable to monitor
counter = 0

# Register the variable for monitoring
watcher.watch(lambda: counter, "counter")

# Start monitoring (samples every 1 second by default)
watcher.start()

# Modify the variable
for i in range(10):
    counter += 1
    time.sleep(1.1)

# Stop monitoring
watcher.stop()

# Access recorded data
print(watcher["counter"])  # Print the recorded values
print(watcher.value_list("counter"))  # Alternative way to get values
print(watcher.time_list())  # Get timestamps
```

### System Resource Monitoring

Monitor CPU and memory usage over time:

```python
from datawatcher import DataWatcher
import psutil  # pip install psutil
import time

# Create watcher instance
watcher = DataWatcher()

# Register system metrics for monitoring
watcher.watch(lambda: psutil.cpu_percent(), "cpu_usage")
watcher.watch(lambda: psutil.virtual_memory().percent, "memory_usage")

# Start monitoring every 1 seconds
watcher.start(interval=1.0)

# Let it run for 10 seconds
print("Monitoring system resources for 10 seconds...")
time.sleep(10)

# Stop monitoring
watcher.stop()

# Display results
print("\n=== System Monitoring Results ===")
print(f"CPU Usage: {watcher['cpu_usage']}")
print(f"Memory Usage: {watcher['memory_usage']}") 
print(f"Timestamps: {watcher.time_list()}")
```

## API Reference

### DataWatcher

Main class for monitoring data changes.

#### Methods

- `watch(func: Callable, key: str)` - Register a function to monitor
- `unwatch(key: str)` - Remove a monitored function
- `clear()` - Clear all monitored functions and history
- `start(interval: float = 1.0)` - Start monitoring with specified interval
- `stop()` - Stop monitoring
- `time_list() -> List[float]` - Get timestamp list
- `value_list(key: str) -> List[Any]` - Get recorded values for a key
- `__getitem__(key: str) -> List[Any]` - Access values using bracket notation


## License

MIT License
