

import time
import requests
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("timecraft_ai")


class Notifier:
    @staticmethod
    def notify_webhook(webhook_url, payload):
        """
        Send a JSON payload to a webhook URL via HTTP POST.
        :param webhook_url: The webhook endpoint URL.
        :param payload: Dictionary to send as JSON.
        """
        if not requests:
            logger.warning(
                "[Webhook] 'requests' library not installed. Cannot send webhook notification."
            )
            return None
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            logger.info(
                f"[Webhook] Notification sent. Status code: {response.status_code}")
        except Exception as e:
            logger.error(f"[Webhook] Error sending notification: {e}")
        return None

    @staticmethod
    def notify_webhook_with_retry(webhook_url, payload, retries=3, delay=5):
        """
        Send a JSON payload to a webhook URL with retry logic.
        :param webhook_url: The webhook endpoint URL.
        :param payload: Dictionary to send as JSON.
        :param retries: Number of retry attempts.
        :param delay: Delay between retries in seconds.
        """
        if not requests:
            logger.warning(
                "[Webhook] 'requests' library not installed. Cannot send webhook notification."
            )
            return None
        for attempt in range(retries):
            try:
                response = requests.post(webhook_url, json=payload, timeout=10)
                if response.status_code == 200:
                    logger.info(
                        f"[Webhook] Notification sent successfully on attempt {attempt + 1}.")
                    return response
                else:
                    logger.warning(
                        f"[Webhook] Attempt {attempt + 1} failed with status code: {response.status_code}")
            except Exception as e:
                logger.error(f"[Webhook] Attempt {attempt + 1} error: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
        return None

    @staticmethod
    def notify_webhook_with_timeout(webhook_url, payload, timeout=10):
        """
        Send a JSON payload to a webhook URL with a timeout.
        :param webhook_url: The webhook endpoint URL.
        :param payload: Dictionary to send as JSON.
        :param timeout: Timeout for the request in seconds.
        """
        if not requests:
            logger.warning(
                "[Webhook] 'requests' library not installed. Cannot send webhook notification."
            )
            return None
        try:
            response = requests.post(
                webhook_url, json=payload, timeout=timeout)
            logger.info(
                f"[Webhook] Notification sent. Status code: {response.status_code}")
            return response
        except requests.Timeout:
            logger.error("[Webhook] Request timed out.")
        except Exception as e:
            logger.error(f"[Webhook] Error sending notification: {e}")
        return None


__all__ = [
    "Notifier",
]
