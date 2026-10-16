---
name: stripe-refunds
description: Issues refunds through the Stripe API for a customer order, partial or full, after checking the order and the refund policy. Use when someone asks to refund an order, give money back, issue a partial refund, or reverse a charge.
---

# Stripe refunds

1. Ask for the order number and whether the refund is full or partial.
2. Look the charge up with the Stripe API. Read
   [references/api-notes.md](references/api-notes.md) for the endpoints and the key.
3. Check the policy: full refunds within 30 days, partial after that, nothing after 90.
4. Show the person the charge, the amount and the reason, and wait for a yes.
5. Create the refund and report the refund id.

## Configuration

None.
