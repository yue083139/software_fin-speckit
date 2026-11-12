"""判定建議（game-mode-framework D4）：參考答案只產生建議，不自動計分（TRD §6 裁定）。"""
import unicodedata
from collections.abc import Sequence

from .guided_notes import Slot


def normalize(text: str) -> str:
    return "".join(unicodedata.normalize("NFKC", text).split()).casefold()


def suggest(answers: Sequence[str], slots: Sequence[Slot]) -> bool | None:
    """各子題正規化後與參考答案全等 ⇒ True；任一不同 ⇒ False；任一子題缺參考答案 ⇒ None。"""
    if not slots or any(s.reference is None for s in slots):
        return None
    return all(normalize(a) == normalize(s.reference or "") for a, s in zip(answers, slots, strict=True))
