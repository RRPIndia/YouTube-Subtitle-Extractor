# Logging helper for yt_rrp


import logging
import os
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

log_path = os.path.join(LOG_DIR, datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_path, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("yt_rrp")

# Example usage throughout your existing script:
#
# logger.info("Program started")
# logger.info(f"Found {len(channels)} channels.")
# logger.info(f"Checking {channel_url}")
# logger.info(f"Processing {file}")
# logger.info(f"Video: {title}")
# logger.info(f"Saved to {filepath}")
# logger.warning("No subtitles available.")
# logger.error("Telegram request failed")
# logger.exception("Unexpected error while processing file")
#
# Replace print(...) with logger.info(...) where appropriate.
#
# In exception handlers, use:
#
# except Exception:
#     logger.exception("Failed processing current video")
#     continue
