from abc import ABC, abstractmethod


class Proxy(ABC):
    """Abstract Base Proxy Class"""

    @abstractmethod
    def forward_request(self, data):
        """Must be implemented by subclasses"""
        pass

    def generate_error_response(self):
        """Generates a professional and user-friendly error message"""
        return {
            "status": "error",
            "message": "Our servers are currently experiencing high traffic or temporary downtime.",
            "suggestion": "Please try again in a few moments. If the issue persists, contact support.",
            "support_email": "support@example.com",
            "retry_after_seconds": 30,
        }, 503
