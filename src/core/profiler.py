import time
from .logger import log


class Profiler:
    def __init__(self, name=None, start=True, log_fn=None):
        self.name = name
        self.start_time = None
        self.last_time = None
        self.count = 0
        self.log_fn = log_fn or log.debug
        if start:
            self.start()

    def start(self):
        """Start a new profiling session."""
        self.start_time = time.time()
        self.last_time = self.start_time
        self.count = 0

    def checkpoint(self, description=""):
        self.log(description, log.debug)

    def debug(self, description=""):
        self.log(description, log.debug)

    def info(self, description=""):
        self.log(description, log.info)

    def warn(self, description=""):
        self.log(description, log.warn)

    def error(self, description=""):
        self.log(description, log.error)

    def log(self, description="", log_fn=None):
        """Mark a new checkpoint and print the time since the last checkpoint."""
        if not log_fn:
            log_fn = log_fn or self.log_fn
        current_time = time.time()
        if self.last_time is None:
            raise RuntimeError(
                "You must start the profiler before setting a checkpoint."
            )

        self.count += 1
        elapsed_since_last = current_time - self.last_time
        elapsed_since_start = current_time - self.start_time
        self.last_time = current_time

        info = (
            self.name + "::" + (isinstance(description, str) or "")
            if self.name
            else description
        )

        if self.count == 1:
            log_fn(f"{info}: {elapsed_since_last:.4f}")
        else:
            log_fn(f"{info}: {elapsed_since_last:.4f} ({elapsed_since_start:.4f}).")

    def stop(self):
        """Stop the current profiling session and print total time."""
        if self.start_time is None:
            raise RuntimeError("You must start the profiler before stopping it.")

        self.count += 1
        total_time = time.time() - self.start_time
        log.info(f"Profiling stopped. Total time: {total_time:.4f} seconds.")
        # Reset the timers
        self.start_time = None
        self.last_time = None
