# Restore log

A backup counts only once it has been restored. Run a scripted restore into a scratch environment every month.

Setup: managed point-in-time recovery, plus a nightly copy of the database and files to object storage in another account with object lock.

| Date | Backup restored | Target | Checks (row counts, checksums, sample items) | Measured RTO | Measured RPO | Problems |
|---|---|---|---|---|---|---|
