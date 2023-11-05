import time

class Profiler:
    def __init__(self, start=True):
        self.start_time = None
        self.last_time = None
        self.count = 0
        if (start):
            self.start()

    def start(self):
        """Start a new profiling session."""
        self.start_time = time.time()
        self.last_time = self.start_time
        self.count = 0

    def checkpoint(self, description=""):
        """Mark a new checkpoint and print the time since the last checkpoint."""
        current_time = time.time()
        if self.last_time is None:
            raise RuntimeError("You must start the profiler before setting a checkpoint.")

        self.count += 1
        elapsed_since_last = current_time - self.last_time
        elapsed_since_start = current_time - self.start_time
        self.last_time = current_time

        if self.count == 1:
            print(f"{description}: {elapsed_since_last:.4f}")
        else:
            print(f"{description}: {elapsed_since_last:.4f} ({elapsed_since_start:.4f}).")

    def stop(self):
        """Stop the current profiling session and print total time."""
        if self.start_time is None:
            raise RuntimeError("You must start the profiler before stopping it.")

        self.count += 1
        total_time = time.time() - self.start_time
        print(f"Profiling stopped. Total time: {total_time:.4f} seconds.")
        # Reset the timers
        self.start_time = None
        self.last_time = None


