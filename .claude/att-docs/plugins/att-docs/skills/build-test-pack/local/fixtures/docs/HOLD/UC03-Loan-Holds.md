# UC03 Loan Holds

Synthetic process description for the local pipeline's tests. It describes no real system.

<a id="page-1"></a>

## Page 1: Borrowing

A patron with a current card may borrow up to five items at the circulation desk.

<a id="page-2"></a>

## Page 2: Holds

A hold on the patron's account blocks every new loan until staff clear the hold. A
current card does not override a hold: the desk shows "Account on hold" and the loan is
refused. The one exception is a supervisor override, which allows one loan despite the
hold and records a reason code.

<a id="page-3"></a>

## Page 3: Loan preferences

On the Loan Preferences page the patron may edit the default loan length. Reset
restores the saved loan length and discards the unsaved edit.
