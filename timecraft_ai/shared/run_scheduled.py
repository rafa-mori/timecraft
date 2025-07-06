"""
Run a function periodically in a background thread.
This module provides a utility to run a specified function at regular intervals
in a separate thread, allowing for periodic tasks without blocking the main application.
#   version   Show the current version of TimeCraftAI
# Example:
#   python -m timecraft_ai status
#
#     if len(sys.argv) < 2:
#         print(HELP) 
#         return
#     command = sys.argv[1]
#     if command == "status":
#         print(f"TimeCraftAI version {VERSION} is running.")
#     elif command == "help":
#         print(HELP)
#     else:
#         print(f"Unknown command: {command}")
#         print("Use 'help' to see available commands.")
# 
"""

from typing import Optional
import logging
import time
import threading

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("timecraft_ai")


class SchedulerService:
    """
    A service to run a function periodically in a background thread.
    This class provides a method to schedule a function to run at specified intervals.
    """

    @staticmethod
    def run_scheduled(
        target_func,
        interval_seconds: int = 60,
        max_runs: Optional[int] = None,
        *args,
        **kwargs,
    ):
        """
        Run a target function periodically in a background thread.
        : param target_func: Function to execute.
        : param interval_seconds: Interval between executions in seconds.
        : param max_runs: Maximum number of executions(None for infinite).
        : param args: Positional arguments for the function.
        : param kwargs: Keyword arguments for the function.
        """

        def _runner():
            run_count = 0
            while max_runs is None or run_count < max_runs:
                logger.info(
                    f"[Scheduler] Running scheduled task: {target_func.__name__} (run {run_count+1})"
                )
                try:
                    target_func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"[Scheduler] Error in scheduled task: {e}")
                run_count += 1
                time.sleep(interval_seconds)

        thread = threading.Thread(target=_runner, daemon=True)
        thread.start()
        return thread

    @staticmethod
    def run_scheduled_with_timeout(
        target_func,
        interval_seconds: int = 60,
        timeout_seconds: int = 10,
        max_runs: Optional[int] = None,
        *args,
        **kwargs,
    ):
        """
        Run a target function periodically with a timeout in a background thread.
        : param target_func: Function to execute.
        : param interval_seconds: Interval between executions in seconds.
        : param timeout_seconds: Timeout for each execution in seconds.
        : param max_runs: Maximum number of executions(None for infinite).
        : param args: Positional arguments for the function.
        : param kwargs: Keyword arguments for the function.
        """

        def _runner():
            run_count = 0
            while max_runs is None or run_count < max_runs:
                logger.info(
                    f"[Scheduler] Running scheduled task with timeout: {target_func.__name__} (run {run_count+1})"
                )
                try:
                    target_func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"[Scheduler] Error in scheduled task: {e}")
                run_count += 1
                time.sleep(interval_seconds)

        thread = threading.Thread(target=_runner, daemon=True)
        thread.start()
        return thread

    @staticmethod
    def run_scheduled_with_webhook(
        target_func,
        interval_seconds: int = 60,
        webhook_url: str = "",
        max_runs: Optional[int] = None,
        *args,
        **kwargs,
    ):
        """
        Run a target function periodically and notify via webhook in a background thread.
        : param target_func: Function to execute.
        : param interval_seconds: Interval between executions in seconds.
        : param webhook_url: Webhook URL to notify after each execution.
        : param max_runs: Maximum number of executions(None for infinite).
        : param args: Positional arguments for the function.
        : param kwargs: Keyword arguments for the function.
        """

        def _runner():
            run_count = 0
            while max_runs is None or run_count < max_runs:
                logger.info(
                    f"[Scheduler] Running scheduled task with webhook: {target_func.__name__} (run {run_count+1})"
                )
                try:
                    result = target_func(*args, **kwargs)
                    if webhook_url:
                        # Assuming result is a dictionary to send as JSON
                        requests.post(webhook_url, json=result)
                except Exception as e:
                    logger.error(f"[Scheduler] Error in scheduled task: {e}")
                run_count += 1
                time.sleep(interval_seconds)

        thread = threading.Thread(target=_runner, daemon=True)
        thread.start()
        return thread


__all__ = [
    "SchedulerService",
]
