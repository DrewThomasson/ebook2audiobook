# Issue 502: a patron with a hold can still borrow

Synthetic defect record for the local pipeline's tests.

## Summary

A patron whose card is current borrows an item even though the account has a hold.
UC03 page 2 says the hold blocks every new loan.

## Change 7002

Change 7002 refuses a new loan while the account has a hold, whatever the card status.
Reset on the Loan Preferences page keeps restoring the saved loan length.
