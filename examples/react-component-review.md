# Example review — React component

A sample review from the `code-review` skill. The change adds a component that
fetches and renders a user's profile bio.

## The change under review

```diff
--- a/src/components/Profile.jsx
+++ b/src/components/Profile.jsx
@@ -1,4 +1,33 @@
 import { useState, useEffect } from "react";

+export function Profile({ userId }) {
+  const [profile, setProfile] = useState(null);
+
+  useEffect(() => {
+    fetch(`/api/users/${userId}`)
+      .then((res) => res.json())
+      .then((data) => setProfile(data));
+  }, []);
+
+  if (!profile) return <div>Loading...</div>;
+
+  return (
+    <div className="profile">
+      <h2>{profile.name}</h2>
+      <div
+        className="bio"
+        dangerouslySetInnerHTML={{ __html: profile.bio }}
+      />
+    </div>
+  );
+}
```

---

## Verdict: Request changes

An XSS sink renders an untrusted bio as raw HTML (Critical), and a stale-closure
`useEffect` dependency bug means the component won't refetch when `userId`
changes (High). There's no error state for a failed fetch. The loading state and
overall structure are good.

## Findings

| ID  | Location                       | Severity | Issue                                                         |
|-----|--------------------------------|----------|---------------------------------------------------------------|
| C1  | `src/components/Profile.jsx:18`| Critical | XSS via `dangerouslySetInnerHTML` of server data (CWE-79)     |
| H1  | `src/components/Profile.jsx:10`| High     | `useEffect` missing `userId` dep — won't refetch on prop change |
| M1  | `src/components/Profile.jsx:6` | Medium   | No error state; failed/rejected fetch leaves it stuck on "Loading…" |
| L1  | `src/components/Profile.jsx:6` | Low      | No cleanup — setState after unmount on a slow response        |

---

## Detail

### [C1] XSS via `dangerouslySetInnerHTML` — `src/components/Profile.jsx:18` — Critical (CWE-79, OWASP A03)

**Why it matters:** `profile.bio` comes from the API (i.e. ultimately from user
input) and is injected as raw HTML. A bio of
`<img src=x onerror="fetch('/api/steal?c='+document.cookie)">` runs attacker
script in every viewer's session. This is stored XSS.

**Fix:** render bio as text, or sanitize it before trusting it as HTML.
```jsx
// simplest — render as text, no HTML at all
<div className="bio">{profile.bio}</div>

// if rich text is genuinely required, sanitize first:
import DOMPurify from "dompurify";
<div
  className="bio"
  dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(profile.bio) }}
/>
```

### [H1] Stale `useEffect` dependency — `src/components/Profile.jsx:10` — High

**Why it matters:** the effect's dependency array is `[]`, so it runs once on
mount and captures the first `userId`. If the parent re-renders `Profile` with a
new `userId` (e.g. navigating between profiles), the component keeps showing the
old user's data and never refetches.

**Fix:** depend on `userId`.
```jsx
useEffect(() => {
  fetch(`/api/users/${userId}`)
    .then((res) => res.json())
    .then(setProfile);
}, [userId]);
```

### [M1] No error state — `src/components/Profile.jsx:6` — Medium

**Why it matters:** there is no `.catch`, and `res.json()` is parsed without
checking `res.ok`. On a network failure or a non-2xx response, `profile` stays
`null` forever and the user is stuck on "Loading…" with no signal. Failed
requests are a realistic, common path.

**Fix:** track an error and check the response.
```jsx
const [error, setError] = useState(null);
// inside the effect:
fetch(`/api/users/${userId}`)
  .then((res) => {
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  })
  .then(setProfile)
  .catch(setError);
// in render:
if (error) return <div role="alert">Couldn't load profile.</div>;
```

### [L1] setState after unmount — `src/components/Profile.jsx:6` — Low

**Why it matters:** if the component unmounts before the fetch resolves, the
`setProfile` call updates state on an unmounted component (wasted work, and a
warning in older React). Use an `ignore` flag or an `AbortController` in the
effect cleanup.

**Fix:**
```jsx
useEffect(() => {
  let ignore = false;
  fetch(`/api/users/${userId}`)
    .then((res) => res.json())
    .then((data) => { if (!ignore) setProfile(data); });
  return () => { ignore = true; };
}, [userId]);
```

---

## What's good

- A loading state is handled up front (`if (!profile) return <div>Loading…</div>`)
  — many implementations forget this.
- State is modeled with hooks cleanly and the JSX is readable.
- The fix for the error state (M1) and the cleanup (L1) compose naturally with the
  `userId` dependency fix (H1) — once the dependency array is right, the rest slots
  into the same effect.
