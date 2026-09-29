import json
from pathlib import Path
from typing import Any, Dict

class TrackedDict(dict):
    """A dictionary subclass that triggers a save callback whenever it is mutated."""
    def __init__(self, *args, save_callback=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.save_callback = save_callback

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if self.save_callback:
            self.save_callback()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        if self.save_callback:
            self.save_callback()

class AutoSaveDict:
    def __init__(self, filename: str):
        self.filename = Path(filename)
        self._data: TrackedDict = None
        self._initialized = False

    def _ensure_loaded(self):
        if not self._initialized:
            if self.filename.exists():
                raw_data = json.loads(self.filename.read_text())
            else:
                raw_data = {}

            # Wrap the raw dictionary in our TrackedDict class and link the callback
            self._data = TrackedDict(raw_data, save_callback=self._save_to_disk)

            # Write initial file if it didn't exist
            if not self.filename.exists():
                self._save_to_disk()

            self._initialized = True

    def __get__(self, instance, owner) -> Dict[str, Any]:
        self._ensure_loaded()
        return self._data

    def __set__(self, instance, value: Dict[str, Any]):
        if not isinstance(value, dict):
            raise TypeError("Config must be a dictionary")
        self._data = TrackedDict(value, save_callback=self._save_to_disk)
        self._initialized = True
        self._save_to_disk()

    def _save_to_disk(self):
        self.filename.write_text(json.dumps(self._data, indent=4))