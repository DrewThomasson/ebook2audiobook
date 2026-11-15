# Issue 501: renewal counts the new expiry from the renewal day

Synthetic defect record for the local pipeline's tests.

## Summary

A card renewed early gets a new expiry three years after the renewal day, so a
patron who renews 20 days before expiry loses 20 days. UC01 page 4 says the new
expiry is three years after the old expiry date.

## Change 7001

Change 7001 computes the new expiry from the old expiry date and records both dates
in the renewal history row. Online and desk renewals both take the fix. The fines
block and the renewal window are unchanged.
