---
name: qbr-prep
description: Runs the QBR-v3 pipeline. Pulls the Halcyon usage export and the renewal sheet, computes adoption deltas with scripts/deltas.py and fills the Halcyon slide template. Use when someone runs qbr-v3 or asks for a Halcyon pack.
---

# QBR prep

1. Ask which account, and for the Halcyon usage export (CSV) and the renewal sheet.
2. Run `scripts/deltas.py usage.csv` for quarter-on-quarter adoption changes.
3. Flag any seat utilisation under 60 per cent as a renewal risk.
4. Fill `templates/halcyon.md`: headline, adoption, risks, asks for next quarter.
5. Hand back the draft. Never send it to the client.

## Configuration

Where the Halcyon exports are saved.
