# Parking Permit Lookup: scaling calculations

The completed design is in
[week6_design/parking_permit_lookup.md](../week6_design/parking_permit_lookup.md).
This analysis uses the supplied `Copy of design_doc_template.md` and Parts
10–15 of `System Design Handbook.docx.md`, both found in Downloads. The source
files in Downloads are unchanged. The reference URL-shortener sections are
available in handbook Part 15; its separate example file was not supplied.

## Inputs and assumptions

The supplied draft names Parking Permit Lookup, estimates 100–500 requests per
second, and requires checks in less than 3 seconds with 99% availability. Its
Capacity and Proposed design sections were blank. The following additions
make those missing inputs explicit; they are proposed values to review with
the pair, not measurements or claims about a running system.

| Input | Value used | Source or assumption |
|---|---|---|
| Baseline peak request rate | 500/second, total of reads and writes | Upper end of the draft's range |
| Peak/average factor | 5 | Added assumption; average is 100/second |
| Read/write ratio | 99:1, at both average and peak | Added assumption |
| Baseline peak reads / writes | 495 / 5 per second | 500 x 0.99 / 500 x 0.01 |
| Baseline average writes | 1/second | 100 x 0.01 |
| Stored bytes per new permit | 400 bytes, including its indexes | Added estimate to measure; VARCHAR maximum lengths do not imply every value uses that space |
| Annual growth | Treat every average write as a new row | Conservative assumption; upserts of existing keys grow less |
| Storage planning horizon | One year, starting empty | Added assumption; longer horizons are shown separately |
| Check logging | No persistent check/audit rows | Added scope assumption; each check performs one read |
| Baseline components | Load balancer, Permit API, Permit database | Added proposed design, because the source section was blank |

The original non-goal "No current connected database" is preserved as a
prototype limitation. The proposed persistent backend is an explicit planning
extension so registration updates have an authoritative source. It has not
been implemented. Employee login and camera recognition remain outside this
exercise. The draft's "1-2 mb/s" does not define units or whether traffic is
persisted, so it cannot be used as annual stored bytes without clarification.

## Capacity at 100 times

Using 365 days/year and decimal units (1 GB = 10^9 bytes, 1 TB = 10^12 bytes):

```text
Average writes           = (500 / 5) / 100 = 1 per second
Rows added/year          = 1 x 86,400 x 365 = 31,536,000
Baseline bytes/year      = 31,536,000 x 400 = 12,614,400,000
Baseline storage/year    = 12.6144 GB

100x peak requests       = 500 x 100 = 50,000 per second
100x peak reads          = 495 x 100 = 49,500 per second
100x peak writes         = 5 x 100 = 500 per second
100x bytes/year          = 12,614,400,000 x 100
                         = 1,261,440,000,000 = 1.26144 TB
Read/write ratio         = 49,500 / 500 = 99:1, unchanged
```

The handbook's Section 10.3 limits are round practice numbers, not measured
capacities. Storage includes the assumed row and index footprint, but excludes
backups, transaction logs, and existing data. Each standby needs its own full
copy; it does not increase the primary's usable storage or serving capacity.

## Load, limits, shares, and machine counts

Start with the proposed baseline of a single database primary, with no cache
or read replicas. A share is the component's load divided by one machine's
limit. API copies can be added without changing the data model; partitioning
the database requires a design change.

| Component / resource | Load at 100x | Limit of one machine, handbook 10.3 | Share | Result |
|---|---:|---:|---:|---|
| Load balancer | 50,000 requests/s | 50,000 requests/s | 1.000 | One active instance reaches its limit; a passive spare provides failover |
| Permit API | 50,000 requests/s | 1,000 requests/s | 50.000 | Minimum 50 copies; select 51 to lose one copy at peak |
| Permit database reads | 49,500 reads/s | 10,000 key reads/s | 4.950 | First bottleneck among components that cannot simply add copies |
| Permit database writes | 500 row changes/s | 5,000 row changes/s | 0.100 | Below the single-primary practice limit |
| Permit database storage | 1.26144 TB after one year | 4 TB | 0.31536 | Fits in year one; without deletion a single disk fills after 3.17 years |

Before changing the design, database reads reach their limit at
10,000/495 = 20.20 times the original peak load. The API's higher numeric share
does not make it the first fixed bottleneck, because the proposed stateless
API can add copies.

## Fix the first bottleneck and find the next

Partition permits by a hash of the normalized `(plate, parking_type)` key,
with the API mapping that key to one primary. This changes the original
single-primary data layout; it is not accomplished by adding read replicas.
Every lookup and update still reaches the authoritative primary for its key.
An acknowledged update must be visible to subsequent checks; asynchronous
replicas or a stale cache could give the wrong permit decision.

The minimum number of primary shards is
max(ceil(49,500/10,000), ceil(500/5,000), ceil(1.26144/4)) = 5.
Five shards would use 99% of each shard's assumed read capacity, so select
**six** for some headroom. Assuming requests and new records distribute evenly:

| Resource per primary after the change | Load | Share of its limit |
|---|---:|---:|
| Key reads | 49,500 / 6 = 8,250/s | 0.825 |
| Row changes | 500 / 6 = 83.33/s | 0.01667 |
| Annual stored bytes | 1.26144 / 6 = 0.21024 TB | 0.05256 after year one |

The next throughput limit is the active Load balancer: 50,000/50,000 = 1 at
100x, and it cannot carry traffic above that point. A second passive balancer
does not raise that ceiling. It would need a separate change, such as traffic
partitioning across independently addressed balancers. With six database
shards, reads reach their aggregate limit at 60,000/495 = 121.21 times the
original load, so they do not precede the balancer's next limit. At fixed
100x traffic with no deletion and balanced data growth, storage fills after
4/(1.26144/6) = **19.03 years** from empty.

Selected machine counts at 100x are 51 API copies, two balancer instances, and
six primary/standby database pairs: 65 machines in total. The API's 51-copy
choice tolerates one failed copy; it does not allow replacing one third of
copies at peak. Applying the handbook's one-third deployment example would
need ceil(50/(2/3)) = 75 API copies instead. No standby capacity is counted as
normal serving throughput.

The even-traffic and 400-byte-row assumptions require measurement. A hot
permit key can saturate one shard even when aggregate capacity is sufficient,
and the read/write practice limits are checked separately rather than being
a benchmark of mixed traffic or synchronous replication. This draft does not
claim the latency or availability targets have been proven by these numbers.

## Four-question review

This is a self-check against the README's review questions; it is not a paired
document swap or a claim that a classmate reviewed the work.

| Question | Answer in the draft |
|---|---|
| First component, with numeric load and limit? | Permit database reads: 49,500/s against 10,000/s, share 4.95 |
| Design change and next bottleneck? | Six authoritative database shards; active balancer next at 50,000 requests/s, exceeding its limit above 100x growth |
| Failure row for every named component? | Yes: Load balancer, Permit API, Permit database |
| Every failure row says what the user sees? | Yes: temporary unavailability is distinguished from a negative permit decision, with the affected request share stated where useful |

The human pair exchange and bringing the document to Session 8 remain
classroom activities.
