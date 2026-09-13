from prometheus_client import Counter, Histogram

notes_created_total = Counter("notes_created_total", "Total created notes")
notes_deleted_total = Counter("notes_deleted_total", "Total deleted notes")
cache_hits_total = Counter("cache_hits_total", "Cache hits")
cache_misses_total = Counter("cache_misses_total", "Cache misses")
request_duration = Histogram(
    "request_duration_seconds", "Request duration", ["method", "endpoint"]
)
