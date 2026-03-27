"""SmartCast TV control layer."""

from pyvizio import Vizio

from remote import config

DEVICE_ID = "remote"
APP_NAME = "remote"

MAX_VOLUME = 100


class VizioRemote:
    def __init__(self, cfg: dict | None = None):
        self.cfg = cfg or config.load()
        self._vizio: Vizio | None = None

    def _get_vizio(self) -> Vizio:
        if self._vizio is None:
            addr = config.get_vizio_addr(self.cfg)
            if not addr:
                raise RuntimeError("TV not configured. Run: tv connect")
            self._vizio = Vizio(
                DEVICE_ID,
                addr,
                APP_NAME,
                auth_token=self.cfg.get("vizio_auth", ""),
                device_type=self.cfg.get("device_type", "tv"),
            )
        return self._vizio

    def _require_addr(self) -> str:
        addr = config.get_vizio_addr(self.cfg)
        if not addr:
            raise RuntimeError("TV IP not configured. Run: tv connect")
        return addr

    # --- Discovery & Pairing ---

    @staticmethod
    def discover(timeout: int = 5) -> list:
        return Vizio.discovery_zeroconf(timeout=timeout)

    def start_pair(self):
        addr = self._require_addr()
        v = Vizio(
            DEVICE_ID,
            addr,
            APP_NAME,
            device_type=self.cfg.get("device_type", "tv"),
        )
        result = v.start_pair()
        if result is None:
            raise RuntimeError("Failed to start pairing. Check TV IP and ensure it is on.")
        return result

    def finish_pair(self, ch_type, token, pin: str):
        addr = self._require_addr()
        v = Vizio(
            DEVICE_ID,
            addr,
            APP_NAME,
            device_type=self.cfg.get("device_type", "tv"),
        )
        result = v.pair(ch_type, token, pin=pin)
        if result is None:
            raise RuntimeError("Pairing failed. Wrong PIN or TV rejected the request.")
        return result.auth_token

    def test_connection(self) -> bool:
        try:
            v = self._get_vizio()
            return v.can_connect_with_auth_check()
        except Exception:
            return False

    # --- Power ---

    def power_on(self) -> bool:
        return bool(self._get_vizio().pow_on())

    def power_off(self) -> bool:
        return bool(self._get_vizio().pow_off())

    def power_toggle(self) -> bool:
        return bool(self._get_vizio().pow_toggle())

    def get_power_state(self) -> bool | None:
        return self._get_vizio().get_power_state()

    # --- Volume ---

    def volume_up(self, steps: int = 1) -> bool:
        return bool(self._get_vizio().vol_up(num=steps))

    def volume_down(self, steps: int = 1) -> bool:
        return bool(self._get_vizio().vol_down(num=steps))

    def get_volume(self) -> int | None:
        return self._get_vizio().get_current_volume()

    def set_volume(self, level: int) -> bool:
        level = max(0, min(level, MAX_VOLUME))
        current = self.get_volume()
        if current is None:
            return False
        diff = level - current
        if diff > 0:
            return self.volume_up(diff)
        elif diff < 0:
            return self.volume_down(abs(diff))
        return True

    def mute(self) -> bool:
        return bool(self._get_vizio().mute_on())

    def unmute(self) -> bool:
        return bool(self._get_vizio().mute_off())

    def mute_toggle(self) -> bool:
        return bool(self._get_vizio().mute_toggle())

    def is_muted(self) -> bool | None:
        return self._get_vizio().is_muted()

    # --- Input / Apps ---

    def launch_app(self, app_name: str) -> bool:
        return bool(self._get_vizio().launch_app(app_name))

    def get_current_app(self) -> str | None:
        return self._get_vizio().get_current_app()

    def get_inputs(self) -> list | None:
        return self._get_vizio().get_inputs_list()

    def set_input(self, input_name: str) -> bool:
        return bool(self._get_vizio().set_input(input_name))

    # --- Navigation Keys ---

    def key(self, key_name: str) -> bool:
        return bool(self._get_vizio().remote(key_name.upper()))

    # --- Info ---

    def get_model(self) -> str | None:
        return self._get_vizio().get_model_name()

    def get_version(self) -> str | None:
        return self._get_vizio().get_version()

    def status(self) -> dict:
        v = self._get_vizio()
        result = {}
        for key, method in [
            ("power", v.get_power_state),
            ("volume", v.get_current_volume),
            ("muted", v.is_muted),
            ("app", v.get_current_app),
            ("input", v.get_current_input),
        ]:
            try:
                result[key] = method()
            except Exception:
                result[key] = None
        return result
