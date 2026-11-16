# Cache benchmark notes

We benchmarked three cache eviction policies (lru, lfu, arc) on the replayed production traffic of one week.
The team lead has to choose the policy for the v2 release by Friday. The memory budget per node is 700 MB.
The p95 and hit-rate numbers in results.csv were measured with the same traffic replay.
