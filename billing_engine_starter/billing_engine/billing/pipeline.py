"""
build_invoice — PURE function that turns inputs into an Invoice dataclass.

⚠️ NO database calls here. No `datetime.now()`. No PDF. Just math.

The order is FIXED:
    1. base       = strategy.calculate(usage)
    2. discount   = discount.apply(base) if discount else 0
    3. taxable    = base - discount
    4. tax        = tax_calc.apply(taxable)
    5. total      = taxable + tax.total
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from billing_engine.money import Money
from billing_engine.models import (
    Invoice, InvoiceStatus, InvoiceLineItem, LineItemKind, Subscription, Plan,
)
from billing_engine.pricing.base import PricingStrategy
from billing_engine.discounts.base import Discount, DiscountContext
from billing_engine.taxes.base import TaxCalculator, TaxContext


def build_invoice(
    subscription: Subscription,
    plan: Plan,
    strategy: PricingStrategy,
    discount: Optional[Discount],
    tax_calc: TaxCalculator,
    tax_context: TaxContext,
    usage_quantity: int,
    period_start: date,
    period_end: date,
    invoice_count_so_far: int,
) -> Invoice:
    """Pure function. Returns an Invoice (id=None, status=DRAFT) ready to be persisted."""
    # TODO Day 2
    #1. Base Charge
    subtotal = strategy.calculate(usage_quantity)
    #2. Discount
    if discount is not None:
        discount_total = discount.apply(subtotal, DiscountContext(invoice_count_so_far=invoice_count_so_far))
    else:
        discount_total = Money.zero(subtotal.currency)
    #3. Taxable Amount
    taxable=subtotal - discount_total
    #4. Taxes
    tax_breakdown = tax_calc.apply(taxable, tax_context)
    #5. Total
    total = taxable + tax_breakdown.total
    line_item = [
        InvoiceLineItem( 
        id=None,
        invoice_id=None,
        description="Base charge",
        amount=subtotal,
        kind=LineItemKind.BASE,
    )
    ]
    if not discount_total.is_zero():
        line_item.append(
            InvoiceLineItem(
                id=None,
                invoice_id=None,
                description="Discount",
                amount=-discount_total,  # negative because it's a discount
                kind=LineItemKind.DISCOUNT,
            )
        )
    if not tax_breakdown.total.is_zero():
        line_item.append(
            InvoiceLineItem(
                id=None,
                invoice_id=None,
                description="Tax",
                amount=tax_breakdown.total,
                kind=LineItemKind.TAX,
            )
        )
    return Invoice(
        id=None,
        subscription_id=subscription.id,
        period_start=period_start,
        period_end=period_end,
        line_items=line_item,
        total=total,
        status=InvoiceStatus.DRAFT,
        line_items=line_items,
    )




        