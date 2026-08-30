# The claim library (template)

**What your own data can settle, and the exact number that settles it.** This
is the ammunition. A reply that carries a measured number is worth ten replies
that carry an opinion, and this file is what makes the first kind fast enough
to write inside the window while a thread is still warm.

Copy this file into your workspace as `CLAIMS.md` and fill it from YOUR data:
your analytics, your scans, your experiments, your customer numbers. Never
inherit someone else's numbers; a claim you cannot defend when the thread
pushes back is worse than no claim.

## The caveat that travels with every number

Write one sentence here describing the scope of your data set: how many
companies or data points, over what period, weighted towards what. Say it in
every reply that uses a number. A number without its scope is a number nobody
should trust, and stating the limit is why yours get believed.

## The shape of a claim

One block per claim, numbered so replies and the ledger can cite it:

```
## C1 <the claim, as one plain sentence>

- trigger: <keyword | phrases | that flag a thread where this might land>
- number: <the measured number, with its unit and its comparison>
- caveat: <the limit of the measurement, stated against your own interest>
```

- `trigger:` lines are pipe-separated keyword matches. A sweep uses them to
  FLAG candidate threads, never to decide; a trigger firing means "one of
  your numbers might be relevant", and reading the thread is still the job.
- A claim whose caveat begins `HELD` is not used in any reply until the hold
  is resolved; if a session is asked to use it anyway, it shows the hold and
  refuses.
- Count claim ids across your reply ledger now and then. A claim that is
  worn out reads as a script; a claim never used may be answering a question
  nobody asks.
