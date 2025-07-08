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

    def __init__(self):
        self.thread: Optional[threading.Thread] = None
        self.max_runs: Optional[int] = None
        self.interval_seconds: int = 60

    def __del__(self):
        """
        Ensure the thread is cleaned up when the service is deleted.
        """
        if self.thread and self.thread.is_alive():
            logger.info("[Scheduler] Stopping scheduled thread.")
            self.thread.join(timeout=1)
            logger.info("[Scheduler] Scheduled thread stopped.")
        else:
            logger.info("[Scheduler] No active scheduled thread to stop.")

    def run(self, target_func, *args, **kwargs):
        """
        Run a target function in a background thread.
        : param target_func: Function to execute.
        : param args: Positional arguments for the function.
        : param kwargs: Keyword arguments for the function.
        """
        if self.thread and self.thread.is_alive():
            logger.warning(
                "[Scheduler] A scheduled task is already running. Please stop it before starting a new one."
            )
            return None

        def _runner():
            logger.info("[Scheduler] Running task: %s", target_func.__name__)
            try:
                target_func(*args, **kwargs)
            except Exception as e:
                logger.error("[Scheduler] Error in scheduled task: %s", e)

        self.thread = threading.Thread(target=_runner, daemon=True)
        self.thread.start()
        return self.thread

    @staticmethod
    def scheduled_run(
        target_func,
        *args,
        interval_seconds: int = 60,
        max_runs: Optional[int] = None,
        **kwargs
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
                    "[Scheduler] Running scheduled task: %s (run %d)",
                    target_func.__name__,
                    run_count + 1,
                )
                try:
                    target_func(*args, **kwargs)
                except Exception as e:
                    logger.error("[Scheduler] Error in scheduled task: %s", e)
                run_count += 1
                time.sleep(interval_seconds)

        thread = threading.Thread(target=_runner, daemon=True)
        thread.start()
        return thread

    @staticmethod
    def run_scheduled_with_timeout(
        target_func,
        *args,
        # timeout_seconds: int = 10,
        interval_seconds: int = 60,
        max_runs: Optional[int] = None,
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
                    "[Scheduler] Running scheduled task with timeout: %s (run %d)",
                    target_func.__name__,
                    run_count + 1,
                )
                try:
                    target_func(*args, **kwargs)
                except Exception as e:
                    logger.error("[Scheduler] Error in scheduled task: %s", e)
                run_count += 1
                time.sleep(interval_seconds)

        thread = threading.Thread(target=_runner, daemon=True)
        thread.start()
        return thread

    @staticmethod
    def run_scheduled_with_webhook(
        target_func,
        *args,
        interval_seconds: int = 60,
        webhook_url: str = "",
        max_runs: Optional[int] = None,
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
                    "[Scheduler] Running scheduled task with webhook: %s (run %d)",
                    target_func.__name__,
                    run_count + 1,
                )
                try:
                    result = target_func(*args, **kwargs)
                    if webhook_url:
                        # Assuming result is a dictionary to send as JSON
                        if isinstance(result, dict):
                            result = {"data": result}
                        else:
                            result = {"result": result}

                        # Send the result to the webhook URL
                        if requests is None:
                            logger.error(
                                "[Scheduler] requests module is not available. Cannot send webhook."
                            )
                        else:
                            logger.info(
                                "[Scheduler] Sending result to webhook: %s", webhook_url
                            )
                        if not webhook_url.startswith("http"):
                            logger.error(
                                "[Scheduler] Invalid webhook URL: %s", webhook_url
                            )
                            return
                        if not result:
                            logger.error(
                                "[Scheduler] No result to send to webhook."
                            )
                            return

                        timeout = kwargs.get("timeout", 10)
                        requests.post(webhook_url, json=result,
                                      timeout=timeout)
                except Exception as e:
                    logger.error("[Scheduler] Error in scheduled task: %s", e)
                run_count += 1
                time.sleep(interval_seconds)

        thread = threading.Thread(target=_runner, daemon=True)
        thread.start()
        return thread


__all__ = [
    "SchedulerService",
]
