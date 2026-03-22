import logging
from pathlib import Path

from gui.main_window import App


def configure_logging():
    try:
        log_dir = Path.home() / "FileDBManagerLogs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "app.log"
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
            handlers=[logging.FileHandler(log_file, encoding="utf-8")],
        )
    except Exception:
        logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    configure_logging()
    try:
        app = App()
        app.mainloop()
    except KeyboardInterrupt:
        pass
