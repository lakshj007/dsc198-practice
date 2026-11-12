# Design document for Parking Permit Lookup

By Laksh, Aaron   ·   10/32/2026

Every section has a size limit. The sections from Context to Risks fit on one page. Scaling and Failure modes are added in Session 7, after Risks.

---

## Context

*This system is used for enforcement staff at UC San Diego to scan students’ license plates for valid parking permits. The employee scans the plate, and receives an output of whether the plate has a corresponding permit or not.*

## Goals

*Three bullets. What the system must do. Each one testable.*

- The system must accurately be able to verify if the plate has a valid permit
- The system must be able to complete the check in a reasonable amount of time
- The system must be able to update itself every time new plates are registered

## Non-goals

*Three bullets. What you have decided not to build, written down so the reader stops asking about it.*

- No current login for employees accessing the system
- No current connected database
- No full UI, just backend

## Non-functional requirements

*One line each. A number in every line.*

|  |  |
| :---- | :---- |
| Latency | \<3 seconds |
| Availability | 99% |
| Scale | 100-500 requests per second, 1-2 mb/s |

Capacity

*Planning assumptions added for Session 7 because this section was blank in
 the downloaded draft; these are estimates for the exercise, not measured traffic.*

- Peak: choose the draft's upper bound of 500 total requests/second and assume
  a 5-times peak factor, giving 100 requests/second on average.
- Reads:writes = 99:1 at both average and peak: 99 lookups + 1 permit upsert
  per second on average; 495 lookups + 5 upserts per second at peak.
- New stored bytes/year, assuming every upsert adds a new 400-byte permit row
  including indexes: 1 x 86,400 x 365 x 400 = 12,614,400,000 bytes = 12.6144 GB.
  Checks are read-only and do not persist the observed timestamp; updates to
  existing permit keys grow less than this conservative new-row estimate.

Use decimal GB/TB and a one-year storage planning horizon. The draft's
undefined "1-2 mb/s" is not used as a rate of persisted data. See
[the calculation notes](../week7_scaling/scaling_calculations.md) for assumptions
and the complete load/limit table.

## API

*Three to five lines. Method, path, what comes back. Say which calls can be repeated without harm.*

```
POST /api/permit-checks
{
	"plate": "9TYV823"
	"parking_type": "SR"
	"observed": "09:23:32@01-02-2026"
}

RESPONSE:
{
	"authorized": 1
	"expiration": "00:00:00@02-01-2026"
	"permit_type": "SR"
}
```

Data model

*One table. What one record holds, and where the records are stored.*

| Field | Type | Notes |
| :---- | :---- | :---- |
| plate | varchar(2048) |  |
| parking\_type | varchar(2048) |  |
| observed | char(19) |  |
| authorized | int |  |
| expiration | char(19) |  |
| permit\_type | varchar(2048) |  |

Proposed design

*Planning assumption: this is a proposed persistent version of the backend for
 this exercise; the original "No current connected database" prototype
 limitation above remains a statement about the current implementation.*

The three components are a **Load balancer**, a **Permit API** running as
stateless copies, and a **Permit database** with one primary relational table
in the baseline design. A lookup follows Load balancer -> Permit API -> Permit
database -> Permit API -> client, reading the current row by normalized
`(plate, parking_type)` and calculating authorization from permit type and
expiration. Proposed registration updates go through the same Load balancer
and Permit API, with `PUT /api/permits/{plate}/{parking_type}` replacing that
key's permit state idempotently before returning success. Lookups use the
primary, with no cache or asynchronous read replica, so an acknowledged permit
update is visible to subsequent checks.

## Alternatives considered

*Two, one line each, with the reason each one was not picked.*

- &nbsp;
- &nbsp;

## Risks

*Three bullets. What you are least sure about.*

- How fast the API would be able to update based on the database
- Improvement to the app as in using a camera to scan the license plate and then parsing based on the image
- &nbsp;

---

## Scaling

At 100 times the assumed load, peak traffic is 50,000 requests/second
(49,500 permit lookups and 500 upserts), while annual new storage is
1.26144 TB and reads:writes stays 99:1.
The Permit database breaks first on reads: 49,500/10,000 = 4.95 of one
machine's limit, while its write share is 500/5,000 = 0.10 and first-year
storage share is 1.26144/4 = 0.31536.
Change the design to hash-partition the full permit key across six database
primaries, each with an authoritative read path: five is the arithmetic
minimum, and six lowers the balanced read load to 8,250/10,000 = 0.825 per
primary.
After that change the Load balancer is the next throughput limit, exactly at
50,000/50,000 = 1.0 at 100 times the original traffic and overloaded above
100 times; its active/passive spare supplies failover, not extra throughput.
The Permit API needs ceil(50,000/1,000) = 50 serving copies, so provision 51
for one-copy failure, two Load balancer instances, and six database standbys
in addition to the six primaries; with no deletion and balanced growth a
primary's 4 TB disk fills after 4/(1.26144/6) = 19.03 years from empty.

## Failure modes

These are proposed protections for the scaled design, not implemented features.
The rows cover the three named components in Proposed design; database
primaries and their standbys are instances of the Permit database component.

| Component | What happens | What the user sees | What the design does |
| :---- | :---- | :---- | :---- |
| Load balancer | A failed active instance interrupts every request until its spare takes over; demand above 50,000 requests/second overloads the active instance. | A temporary connection error or "Permit check unavailable; try again"; overload returns 503 rather than an incorrect permit decision. | Use two instances in active/passive failover, each sized for the full peak; monitor failover and saturation, and reject excess traffic promptly. The pair still has only 50,000 requests/second of serving capacity. |
| Permit API | Requests routed to one crashed copy fail until it is removed; with even traffic this is initially about 1/51 of requests. | Some staff see "Permit check unavailable; try again" while other checks continue; a failed check is never displayed as an invalid permit. | Check health every 5 seconds and remove a copy after 2 failed checks, at most 10 seconds for an immediate failed probe; 50 remaining copies carry peak. Use a 2.5-second request deadline and a 500 ms database-call timeout; allow at most one jittered retry for a read, within the deadline, and suppress retries during overload. |
| Permit database | A failed primary stops reads and updates for its shard, about 1/6 of keys under balanced traffic; the other five shards continue. | Affected checks report "Permit status unavailable" and registration updates are not confirmed until committed. No stale response or outage is treated as "no valid permit." | Keep a synchronous standby per primary, fence the former primary before promotion, and serve the shard only when authoritative state is available. Retry the same idempotent PUT only if a newer permit update cannot be overwritten; otherwise reconcile the current state first. Use database timeouts and monitor per-shard read load, storage, and replication health. |
