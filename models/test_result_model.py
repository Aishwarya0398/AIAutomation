from pydantic import BaseModel
from typing import List

class TestResult(BaseModel):
    login_status: str
    cart_items: List[str] = []  # ✅ Store cart items directly, no cart_status
    checkout_status: str
    total_update_status: str
    delivery_location_status: str
    confirmation_message: str
