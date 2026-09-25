

## B2c — Dangerous Patterns
1. self.save() inside validate()

Why: validate() is already part of the save process. Calling self.save() again causes recursive saving.

2. Stock is updating inside validate()

Why: validate() should validate or calculate data. tock deduction should happen only after successful submission.

def validate(self):
    self.packaging_total = sum(r.total_price for r in self.packaging_used)

Stock deduction should be done in on_submit().

## B2d — Concurrency

Why: If two users edit the same document, the second user's copy becomes outdated after the first user saves. Frappe detects this and shows "Document has been modified after you have opened it" to prevent silent overwriting.

## C3 — Rider Rename
frappe.rename_doc("Rider", old, new, merge=False)

Why: assigned_rider is a Link field, so Frappe updates linked references when the Rider name changes.

merge=True is dangerous because it can merge two Rider records instead of simply renaming one.

## D2 — frappe.get_all()

Why: frappe.get_all() can bypass normal permission checks. In a whitelisted API, a low-privilege user could access records they should not see.

Use frappe.get_list() because it fetches the records which have permissions.

## E1 — on_update() Recursion

Reason : self.save() triggers on_update() again, causing infinite recursion and we get RecursionError.


## H1 — frappe.call() in validate

Why: frappe.call() takes some time to get the response from the server. But validate() does not wait for that response. So use frappe.call() in onload or refresh when you need to fetch data.

## I1 — SQL Parameterization
F-string
query = f"""SELECT name, customer_name, delivery_zone FROM `tabDelivery Order` WHERE delivery_zone = '{delivery_zone}'"""

Parameterized
query = """SELECT name, customer_name, delivery_zone FROM `tabDelivery Order` WHERE delivery_zone = %(delivery_zone)s"""

Why parameterized is preferred is because the value is kept separate from the SQL query, reducing SQL injection risk and handling input safely.

## J1 — Jinja vs before_print()

Avoid database queries directly in Jinja:

{% set data = frappe.get_all("Some DocType") %}

Precompute the value in before_print():

def before_print(self, print_settings):
    self.print_summary = f"{self.customer_name} - {self.delivery_zone}"

Then use:

{{ doc.print_summary }}

before_print() handles the data and business logic in Python, while Jinja is only used to display the prepared data.