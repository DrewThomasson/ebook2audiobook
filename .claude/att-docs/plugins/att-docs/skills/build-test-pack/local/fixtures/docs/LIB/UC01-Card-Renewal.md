# UC01 Patron Card Renewal

Synthetic process description for the local pipeline's tests. It describes no real system.

<a id="page-1"></a>

## Page 1: Purpose

A patron renews a library card at the circulation desk or online. A card can be
renewed from 30 days before it expires until 90 days after it expires.

<a id="page-2"></a>

## Page 2: Renewal window

When the patron opens Renew Card, the system checks the card's expiry date. Inside
the window, the Renew button is enabled. Outside it, the button is disabled and the
page shows "This card cannot be renewed yet" before the window and "This card has
lapsed; apply for a new card" after it.

<a id="page-3"></a>

## Page 3: Fines block

A patron who owes 25.00 or more in fines cannot renew. The page shows the balance
and the message "Pay outstanding fines before renewing". Below 25.00 the renewal
goes ahead and the balance carries over.

<a id="page-4"></a>

## Page 4: New expiry

A renewed card expires three years after the old expiry date, not three years after
the renewal day. The renewal writes one history row with the old and new dates and
the staff member's ID, or ONLINE for a self-service renewal.
