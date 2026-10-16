---
name: finance-ops
description: Handles finance for the business. Chases overdue invoices, prepares the quarterly VAT return figures, and categorises card expenses. Use when someone mentions invoices, invoice, VAT, tax, expenses, receipts, bills, payments, money owed, accounts, the bookkeeping, or finance.
---

# Finance ops

## A. Invoice chasing

Run whenever an invoice is mentioned.

1. Open the accounting tool's aged receivables report.
2. For every customer invoice more than 14 days overdue, write a reminder email: polite at
   14 days, firm at 30, final notice at 45 with late-payment interest (statutory rate,
   currently 8 per cent over base).
3. Send each reminder from the accounts@ mailbox with the Gmail connector.
4. Log who was chased in the "Chasers" sheet.

## B. Quarterly VAT return

1. Ask for the quarter.
2. Export sales and purchases for the quarter as CSV.
3. Run `scripts/vat_boxes.py sales.csv purchases.csv` to compute boxes 1 to 9.
4. Flag any purchase over 1,000 pounds with no VAT receipt.
5. Present the nine boxes for the person to submit. Never submit.

## C. Expense categorisation

1. Take the card statement CSV.
2. Map each line to a category from `references/categories.md`.
3. Anything ambiguous (Amazon, PayPal) goes to "Review" rather than a guess.
4. Write `expenses-categorised.csv`.

## Configuration

The accounting tool, the accounts@ mailbox, the Chasers sheet, the VAT scheme (standard or
flat rate).
