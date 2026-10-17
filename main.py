import logging

from monitor import BitcoinMonitor

ENABLE_LOGGING = True

if ENABLE_LOGGING:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    )
else:
    logging.basicConfig(level=logging.CRITICAL)


if __name__ == "__main__":
    monitor = BitcoinMonitor()
    monitor.run()
