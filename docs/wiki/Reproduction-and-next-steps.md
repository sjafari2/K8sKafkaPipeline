# Reproduction and next steps

This is a research implementation for streaming graph analysis. Its former dependency list is not a currently validated installation recipe. Begin from a fixed revision, preserve source and logs, and validate the environment before launching workloads.

1. Select the `v1.0` tag or another recorded commit. Record the full SHA; do not silently replace a historical version with a newer one.
2. Inspect `dockerfiles/`, package manifests, Kafka Helm values, namespace, service endpoints, resource requests, and storage claims. Reconcile configuration copies under `k8s/`, `helm/`, and `dockerfiles/`.
3. Correct and test the launcher issues listed in Findings-and-limitations before using `runPipeline.sh`. Review individual scripts for image cleanup, restarts, and cluster changes. The existing top-level launcher is not a validated one-command deployment.
4. Use a small controlled synthetic text snapshot with known word co-occurrences. Check producer records, consumed records, sparse matrix entries, local fingerprints, and final merge output against expected values.
5. Add explicit snapshot and batch identifiers, expected batch manifests, completion markers, duplicate accounting, and restart tests. Define retry and commit behavior before claiming delivery guarantees.
6. Reconstruct performance evaluation only with preserved configuration, timing boundaries, input counts, acknowledgments, final completeness, clustering fitness, and CPU/memory measurements. Keep source collection size distinct from processed volume.

Actual output directories are constructed from configuration variables in the application and merge scripts, including `local_clstr_path` and `merge_path`. Do not assume every output is in `./request-data` merely because the former README said so.

The later RealTime-Streaming-Pipeline research is related follow-on work. Its newer synthetic workloads, latency definitions, scaling trials, and numerical results must remain separately identified; they are not retrospective measurements of this graph-clustering project.
