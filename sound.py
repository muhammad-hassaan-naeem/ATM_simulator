"""
sound.py — cross-platform audio playback using pygame.mixer.

pygame.mixer works on Windows, macOS and Linux without extra system
packages, replacing the brittle playsound==1.2.2 dependency.

If pygame is not installed (or mixer init fails on a headless system)
every call is a silent no-op so the rest of the app keeps running.
"""

import threading
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ── initialise mixer once at import time ─────────────────────────────────────
_mixer_ok = False
try:
    import pygame
    pygame.mixer.init()
    _mixer_ok = True
    logger.info("pygame.mixer initialised successfully")
except Exception as exc:
    logger.warning("pygame.mixer not available — audio disabled: %s", exc)


def play_sound(path: str) -> None:
    """
    Play a WAV file in a background daemon thread.
    path may be relative (resolved from the project root) or absolute.
    """
    if not _mixer_ok:
        return

    def _play():
        try:
            resolved = _resolve(path)
            if not resolved.exists():
                logger.warning("Sound file not found: %s", resolved)
                return
            sound = pygame.mixer.Sound(str(resolved))
            sound.play()
            # Wait for playback to finish so the thread can exit cleanly
            while pygame.mixer.get_busy():
                time.sleep(0.05)
        except Exception as exc:
            logger.error("play_sound error (%s): %s", path, exc)

    threading.Thread(target=_play, daemon=True).start()


def delayed_sound(path: str, delay: float = 0.5) -> None:
    """Play a sound after a short delay (non-blocking)."""
    if not _mixer_ok:
        return

    def _run():
        time.sleep(delay)
        play_sound(path)

    threading.Thread(target=_run, daemon=True).start()


def play_sound_blocking(path: str) -> None:
    """
    Play a sound and BLOCK until it finishes.
    Used for the exit/logout farewell sound before the window closes.
    """
    if not _mixer_ok:
        return
    try:
        resolved = _resolve(path)
        if not resolved.exists():
            logger.warning("Sound file not found: %s", resolved)
            return
        sound = pygame.mixer.Sound(str(resolved))
        sound.play()
        while pygame.mixer.get_busy():
            time.sleep(0.05)
    except Exception as exc:
        logger.error("play_sound_blocking error (%s): %s", path, exc)


def _resolve(path: str) -> Path:
    """Resolve a path relative to the project root (directory of this file)."""
    p = Path(path)
    if p.is_absolute():
        return p
    return Path(__file__).parent / p
