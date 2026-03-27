"""Virtual TV keyboard navigation."""

import threading
import time

# YouTube keyboard layout:
#   Row 0: A B C D E F G [⌫]
#   Row 1: H I J K L M N [&123]
#   Row 2: O P Q R S T U [⊕]
#   Row 3: V W X Y Z - '
#   7 letter columns

YOUTUBE_LAYOUT = {
    "cols": 7,
    "chars": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "extra": {"-": (3, 5), "'": (3, 6)},
    "row_offset": 0,
    "search": (4, 2),  # SEARCH button on bottom row
}

# Netflix keyboard layout:
#   Row 0: [space] [⌫]
#   Row 1: a b c d e f
#   Row 2: g h i j k l
#   Row 3: m n o p q r
#   Row 4: s t u v w x
#   Row 5: y z 1 2 3 4
#   Row 6: 5 6 7 8 9 0
#   6 columns, letters start at row 1

NETFLIX_LAYOUT = {
    "cols": 6,
    "chars": "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890",
    "extra": {},
    "row_offset": 1,
}

DELAY_KEYS = 0.10
DELAY_CHAR = 0.18

# Global cancel flag — set from any thread to halt typing/clearing
_cancel = threading.Event()


def cancel():
    """Signal any running type_text or clear_text to stop immediately."""
    _cancel.set()


def _check() -> bool:
    """Return True if cancelled. Clears the flag."""
    if _cancel.is_set():
        _cancel.clear()
        return True
    return False


def _build_map(chars: str, cols: int, row_offset: int = 0, extra: dict | None = None) -> dict:
    m = {}
    for i, ch in enumerate(chars):
        m[ch] = (row_offset + i // cols, i % cols)
    if extra:
        m.update(extra)
    return m


def _detect_layout(remote) -> dict:
    try:
        app = remote.get_current_app()
        if app and "youtube" in app.lower():
            return YOUTUBE_LAYOUT
    except Exception:
        pass
    return NETFLIX_LAYOUT


def clear_text(remote, count: int = 30, app: str | None = None) -> None:
    """Clear the TV search field by spamming backspace key presses."""
    _cancel.clear()
    for _ in range(count):
        if _check():
            return
        remote.key("BACK")
        time.sleep(DELAY_KEYS)


def type_text(remote, text: str, app: str | None = None, on_char=None) -> None:
    """Type text on the TV's virtual keyboard.

    IMPORTANT: cursor must be on A (top-left letter) before calling this.
    Halts immediately if cancel() is called.
    """
    _cancel.clear()
    text = text.upper().strip()
    if not text:
        return

    if app and "youtube" in app.lower():
        layout = YOUTUBE_LAYOUT
    elif app and "netflix" in app.lower():
        layout = NETFLIX_LAYOUT
    else:
        layout = _detect_layout(remote)

    cols = layout["cols"]
    row_offset = layout.get("row_offset", 0)
    char_map = _build_map(layout["chars"], cols, row_offset, layout.get("extra"))

    cur_row = row_offset
    cur_col = 0

    for idx, ch in enumerate(text):
        if _check():
            return

        if ch == " ":
            continue

        target = char_map.get(ch)
        if target is None:
            continue

        tr, tc = target

        # Vertical
        if tr > cur_row:
            for _ in range(tr - cur_row):
                if _check():
                    return
                remote.key("DOWN")
                time.sleep(DELAY_KEYS)
        elif tr < cur_row:
            for _ in range(cur_row - tr):
                if _check():
                    return
                remote.key("UP")
                time.sleep(DELAY_KEYS)

        # Horizontal
        if tc > cur_col:
            for _ in range(tc - cur_col):
                if _check():
                    return
                remote.key("RIGHT")
                time.sleep(DELAY_KEYS)
        elif tc < cur_col:
            for _ in range(cur_col - tc):
                if _check():
                    return
                remote.key("LEFT")
                time.sleep(DELAY_KEYS)

        if _check():
            return

        # Select
        remote.key("OK")
        time.sleep(DELAY_CHAR)

        cur_row, cur_col = tr, tc

        if on_char:
            on_char(ch, idx, len(text))
