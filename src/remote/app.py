"""Floating window app using pywebview."""

import os
import sys
import threading

import webview

from remote.api import Api

UI_PATH = os.path.join(os.path.dirname(__file__), "ui", "index.html")

_window = None


def run():
    global _window
    api = Api()
    api._close_window = _close_window
    api._minimize_window = _minimize_window
    _window = webview.create_window(
        "Remote",
        url=UI_PATH,
        js_api=api,
        width=500,
        height=640,
        min_size=(480, 600),
        on_top=True,
        background_color="#080808",
        frameless=True,
        easy_drag=False,
    )
    webview.start(debug=False)


def _close_window():
    def _do():
        try:
            if _window:
                _window.destroy()
        except Exception:
            pass
        os._exit(0)
    threading.Thread(target=_do, daemon=True).start()


def _minimize_window():
    try:
        if _window:
            _window.minimize()
    except Exception:
        pass


if __name__ == "__main__":
    run()
