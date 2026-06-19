"""
FixedAmountDiscount — e.g., flat ₹500 off.

CAPPING RULE: if the fixed amount exceeds the subtotal, return subtotal
(so the discounted total never goes below zero).
"""

from billing_engine.money import Money
from billing_engine.discounts.base import Discount, DiscountContext


class FixedAmountDiscount(Discount):
    def __init__(self, amount: Money) -> None:
        if amount.is_negative():
            raise ValueError("FixedAmountDiscount amount must be non-negative")
        # TODO Day 1
        self._amount = amount

    def apply(self, subtotal: Money, context: DiscountContext) -> Money:
        if self._amount.currency != subtotal.currency:
            raise ValueError("currency mismatch")
            if self._amount< subtotal:
                return self._amount
            else:
                return subtotal
        # TODO Day 1
    
