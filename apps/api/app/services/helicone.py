# Helicone integration for llm-eval-guardrails-platform

import httpx
from typing import Dict, Any, List
import os

class HeliconeService:
    def __init__(self):
        self.api_key = os.getenv("HELICONE_API_KEY")
        self.base_url = "https://api.helicone.ai/v1"
        self.client = httpx.Client(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )

    def log_request(self, request_data: Dict[str, Any]):
        """Log a request to Helicone"""
        response = self.client.post(
            f"{self.base_url}/request/log",
            json=request_data
        )
        return response.json()

    def get_metrics(self, filters: Dict[str, Any] = None):
        """Get metrics from Helicone"""
        params = filters or {}
        response = self.client.get(
            f"{self.base_url}/metrics",
            params=params
        )
        return response.json()

    def get_requests(self, limit: int = 100, offset: int = 0):
        """Get requests from Helicone"""
        response = self.client.get(
            f"{self.base_url}/requests",
            params={"limit": limit, "offset": offset}
        )
        return response.json()

    def get_request(self, request_id: str):
        """Get a specific request by ID"""
        response = self.client.get(
            f"{self.base_url}/request/{request_id}"
        )
        return response.json()

    def get_user_metrics(self, user_id: str):
        """Get metrics for a specific user"""
        response = self.client.get(
            f"{self.base_url}/user/{user_id}/metrics"
        )
        return response.json()

    def get_user_requests(self, user_id: str, limit: int = 100):
        """Get requests for a specific user"""
        response = self.client.get(
            f"{self.base_url}/user/{user_id}/requests",
            params={"limit": limit}
        )
        return response.json()

    def create_alert(self, alert_config: Dict[str, Any]):
        """Create an alert in Helicone"""
        response = self.client.post(
            f"{self.base_url}/alert",
            json=alert_config
        )
        return response.json()

    def get_alerts(self):
        """Get all alerts"""
        response = self.client.get(f"{self.base_url}/alerts")
        return response.json()

    def get_cost(self, start_date: str, end_date: str):
        """Get cost information for a date range"""
        response = self.client.get(
            f"{self.base_url}/cost",
            params={"start_date": start_date, "end_date": end_date}
        )
        return response.json()
