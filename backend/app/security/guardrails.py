import re


class Guardrails:
    def __init__(self):
        # Denylist for topics we don't want to discuss
        self.input_denylist = [
            "competitor", "politics", "election", "president",
            "ignore previous instructions", "system prompt",
            "jailbreak", "override", "disregard", "forget your",
            "pretend you are", "act as", "roleplay", "you are now",
            "ignore all", "bypass", "hack", "exploit",
            "write code", "write a script", "write python",
            "generate code", "show me code"
        ]

        # Patterns that indicate prompt injection attempts
        self.injection_patterns = [
            r'(?i)ignore\s+(?:all\s+)?(?:previous|above|prior)',
            r'(?i)new\s+instructions?:',
            r'(?i)you\s+(?:are|must)\s+now',
            r'(?i)(?:reveal|show|print|output)\s+(?:your|the)\s+(?:system\s+)?prompt',
        ]
        
    def check_input(self, text: str) -> bool:
        """
        Returns False if the input violates guardrails.
        """
        text_lower = text.lower()
        for phrase in self.input_denylist:
            if phrase in text_lower:
                return False
                
        # Check for prompt injection patterns
        for pattern in self.injection_patterns:
            if re.search(pattern, text):
                return False

        # Basic check for repeated characters often used in jailbreaks
        if re.search(r'(.)\1{10,}', text):
            return False
            
        return True

    def check_output(self, text: str) -> bool:
        """
        Returns False if the output violates guardrails.
        """
        text_lower = text.lower()
        # Ensure it didn't leak the system prompt
        if "you are safex assistant" in text_lower:
            return False
        if "rules you must follow" in text_lower:
            return False
            
        # Check for code output
        if "```" in text:
            return False
        if re.search(r'(?:def |class |import |print\(|console\.log)', text):
            return False

        # Basic denylist check on output too
        for word in ["competitor", "politics"]:
            if word in text_lower:
                return False
                
        return True

    def sanitize_rejected_input(self) -> str:
        """Returns a safe rejection message."""
        return "I can only help with SafeX Solutions related questions. How can I assist you with our services?"


guardrails = Guardrails()

