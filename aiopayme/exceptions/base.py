from dataclasses import dataclass, field
from .messages import MESSAGES


@dataclass
class PaymeError(Exception):
    code: int
    lang: str = "ru"
    _message: str = field(default=None, repr=False)

    @property
    def message(self):
        if self._message:
            return self._message
        msgs = MESSAGES.get(self.code, {})
        return msgs.get(self.lang, msgs.get("en", "Unknown error"))

    def to_dict(self):
        return {
            "error": {
                "code": self.code,
                "message": {
                    "ru": MESSAGES.get(self.code, {}).get("ru", ""),
                    "en": MESSAGES.get(self.code, {}).get("en", ""),
                    "uz": MESSAGES.get(self.code, {}).get("uz", ""),
                }
            }
        }