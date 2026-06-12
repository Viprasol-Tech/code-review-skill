# Example review — Python FastAPI endpoint

This is a sample of the review the `code-review` skill produces. The diff under
review adds an endpoint that returns a user's orders.

## The change under review

```diff
--- a/app/api/orders.py
+++ b/app/api/orders.py
@@ -1,6 +1,38 @@
 from fastapi import APIRouter, Depends
 from app.db import get_conn
+from app.auth import get_current_user

 router = APIRouter()

+@router.get("/users/{user_id}/orders")
+def list_orders(user_id: int):
+    conn = get_conn()
+    cur = conn.cursor()
+    cur.execute(f"SELECT id FROM orders WHERE user_id = {user_id}")
+    order_ids = [row[0] for row in cur.fetchall()]
+
+    orders = []
+    for oid in order_ids:
+        cur.execute(f"SELECT id, total, status FROM order_items WHERE order_id = {oid}")
+        items = cur.fetchall()
+        orders.append({"id": oid, "items": items})
+    return {"orders": orders}
```

---

## Verdict: Request changes

Two security defects (SQL injection and missing authorization) make this unsafe
to merge; there is also a clear performance problem. The shape of the response is
fine and the route naming is good.

## Findings

| ID  | Location              | Severity | Issue                                                    |
|-----|-----------------------|----------|----------------------------------------------------------|
| C1  | `app/api/orders.py:11`| Critical | SQL injection via f-string query (CWE-89, OWASP A03)     |
| C2  | `app/api/orders.py:17`| Critical | Second SQL injection in the items query (CWE-89)         |
| H1  | `app/api/orders.py:8` | High     | No authorization check — any user can read any user's orders (IDOR, CWE-639) |
| M1  | `app/api/orders.py:14`| Medium   | N+1 query: one query per order inside the loop           |
| L1  | `app/api/orders.py:9` | Low      | DB connection/cursor never closed — leak on every call   |
| N1  | `app/api/orders.py:18`| Nit      | Returning raw DB tuples instead of named fields          |

---

## Detail

### [C1] SQL injection — `app/api/orders.py:11` — Critical (CWE-89, OWASP A03)

**Why it matters:** `user_id` is interpolated directly into the SQL string with
an f-string. Although the path declares `user_id: int`, the same pattern will be
copied for string params, and even here a crafted value can be abused if the type
coercion is ever relaxed. Parameterize unconditionally — never build SQL by
interpolation.

**Fix:**
```python
cur.execute("SELECT id FROM orders WHERE user_id = %s", (user_id,))
```

### [C2] SQL injection — `app/api/orders.py:17` — Critical (CWE-89)

**Why it matters:** same defect with `oid`. Even though `oid` comes from the DB
here, keep the codebase consistent: all queries parameterized, no exceptions.

**Fix:**
```python
cur.execute(
    "SELECT id, total, status FROM order_items WHERE order_id = %s", (oid,)
)
```

### [H1] Missing authorization — `app/api/orders.py:8` — High (IDOR, CWE-639, OWASP A01)

**Why it matters:** the endpoint takes `user_id` from the URL and returns that
user's orders with no check that the caller *is* that user (or is an admin). Any
authenticated user can enumerate `user_id` and read everyone's orders — a classic
Insecure Direct Object Reference. The `get_current_user` import was added but
never used.

**Fix:** require the current user and verify ownership.
```python
@router.get("/users/{user_id}/orders")
def list_orders(user_id: int, current=Depends(get_current_user)):
    if current.id != user_id and not current.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    ...
```

### [M1] N+1 query — `app/api/orders.py:14` — Medium

**Why it matters:** for a user with *k* orders this issues *1 + k* queries. At
scale that's a round-trip per order on a hot endpoint. Fetch the items in one
query with an `IN` / join and group in memory — `O(1)` queries instead of `O(k)`.

**Fix (sketch):**
```python
cur.execute(
    "SELECT order_id, id, total, status FROM order_items WHERE order_id = ANY(%s)",
    (order_ids,),
)
by_order = defaultdict(list)
for order_id, *item in cur.fetchall():
    by_order[order_id].append(item)
orders = [{"id": oid, "items": by_order[oid]} for oid in order_ids]
```

### [L1] Resource leak — `app/api/orders.py:9` — Low

**Why it matters:** the connection and cursor are never closed; on a long-running
process this leaks connections until the pool is exhausted. Use a context manager
or a FastAPI dependency that closes the connection in a `finally`.

**Fix:** acquire the connection via a `with` block or a dependency that yields and
closes it.

### [N1] Raw tuples in the response — `app/api/orders.py:18` — Nit

The items come back as bare tuples, so the JSON is positional. Map to named keys
(`{"id":…, "total":…, "status":…}`) for a stable, self-documenting API. Not a
blocker; a formatter won't catch it, but it's a one-time cleanup.

---

## What's good

- The route is named with proper REST nesting (`/users/{user_id}/orders`) — clear
  and conventional.
- Authentication was *intended* — the `get_current_user` import shows the right
  instinct; it just wasn't wired in (see H1).
- The response shape (orders containing items) is a sensible aggregate for the
  caller, so once the queries are fixed the contract is good.
