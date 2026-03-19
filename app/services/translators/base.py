# addon: 번역 엔진 공통 인터페이스
# TRANSLATION_ENABLED = True 시 각 엔진이 이 인터페이스를 구현한다.

class BaseTranslator:
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        raise NotImplementedError

    def translate_segments(self, segments: list[str], source_lang: str, target_lang: str) -> list[str]:
        return [self.translate_text(s, source_lang, target_lang) for s in segments]
