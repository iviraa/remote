"""API bridge for pywebview JavaScript."""

import threading

from remote import config
from remote.vizio_remote import VizioRemote


class Api:
    def __init__(self):
        self._remote: VizioRemote | None = None
        self._lock = threading.Lock()
        self._close_window = None
        self._minimize_window = None

    def close_window(self):
        if self._close_window:
            self._close_window()

    def minimize_window(self):
        if self._minimize_window:
            self._minimize_window()

    def _get_remote(self) -> VizioRemote:
        if self._remote is None:
            cfg = config.load()
            self._remote = VizioRemote(cfg)
        return self._remote

    # --- Setup/Connect ---

    def is_configured(self) -> bool:
        return config.is_configured(config.load())

    def discover_tvs(self) -> list[dict]:
        try:
            devices = VizioRemote.discover(timeout=8)
            return [{"name": d.name, "ip": d.ip, "port": d.port, "model": d.model} for d in devices]
        except Exception as e:
            return [{"error": str(e)}]

    def start_pairing(self, ip: str, port: int = 7345) -> dict:
        try:
            cfg = config.load()
            cfg["vizio_ip"] = ip
            cfg["vizio_port"] = port
            config.save(cfg)
            remote = VizioRemote(cfg)
            result = remote.start_pair()
            self._pair_data = {"ch_type": result.ch_type, "token": result.token, "cfg": cfg}
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def finish_pairing(self, pin: str) -> dict:
        try:
            pd = self._pair_data
            remote = VizioRemote(pd["cfg"])
            auth_token = remote.finish_pair(pd["ch_type"], pd["token"], pin)
            cfg = pd["cfg"]
            cfg["vizio_auth"] = auth_token
            config.save(cfg)
            self._remote = None
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # --- Media Controls (via remote keys) ---

    def media_pause(self) -> dict:
        try:
            self._get_remote().key("PAUSE")
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def media_resume(self) -> dict:
        try:
            self._get_remote().key("PLAY")
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def media_stop(self) -> dict:
        try:
            self._get_remote().key("PAUSE")
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # --- Remote ---

    def tv_status(self) -> dict:
        try:
            return self._get_remote().status()
        except Exception as e:
            return {"error": str(e)}

    def volume_up(self, steps: int = 1) -> dict:
        try:
            self._get_remote().volume_up(steps)
            vol = self._get_remote().get_volume()
            return {"ok": True, "volume": vol}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def volume_down(self, steps: int = 1) -> dict:
        try:
            self._get_remote().volume_down(steps)
            vol = self._get_remote().get_volume()
            return {"ok": True, "volume": vol}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def set_volume(self, level: int) -> dict:
        try:
            self._get_remote().set_volume(level)
            return {"ok": True, "volume": level}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def mute(self) -> dict:
        try:
            self._get_remote().mute()
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def unmute(self) -> dict:
        try:
            self._get_remote().unmute()
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def power_on(self) -> dict:
        try:
            self._cancel_automation()
            self._get_remote().power_on()
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def power_off(self) -> dict:
        try:
            self._cancel_automation()
            self._get_remote().power_off()
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def power_toggle(self) -> dict:
        try:
            self._cancel_automation()
            self._get_remote().power_toggle()
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def launch_app(self, app_name: str) -> dict:
        try:
            self._get_remote().launch_app(app_name)
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _cancel_automation(self):
        from remote.tv_keyboard import cancel
        cancel()

    def send_key(self, key: str) -> dict:
        try:
            if key.lower() in ("home", "back"):
                self._cancel_automation()
            self._get_remote().key(key)
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def type_on_tv(self, text: str) -> dict:
        try:
            from remote.tv_keyboard import type_text
            type_text(self._get_remote(), text)
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def clear_tv_text(self, count: int = 30) -> dict:
        try:
            from remote.tv_keyboard import clear_text
            clear_text(self._get_remote(), count=count)
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}
