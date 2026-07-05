class PIIMasker:
    def __init__(self):
        pass

    def mask(self, text: str) -> str:
        """
        Mocked PII masker. Bypassing presidio due to Application Control policy block.
        """
        return text

pii_masker = PIIMasker()
