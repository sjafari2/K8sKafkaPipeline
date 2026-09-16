# Reported findings and limitations

Source: supplied Research.gov award 1807563 final annual report preview, pp. 2-4. These are historical report findings, not experiments rerun in September 2026.

## Pipeline findings

The project established a containerized, multi-stage streaming graph-analysis pipeline on Nautilus. The report describes difficulties transferring producer data reliably to consumers, with missing data affecting clustering quality. It does not quantify a pipeline loss percentage or establish a single root cause. The observation therefore cannot support a general claim that Kafka inherently loses data.

The report proposes further exploration of sequence tagging to identify, track, and verify batches throughout the pipeline. It does not demonstrate a completed, validated end-to-end exactly-once protocol. Waiting for a quiet filesystem interval is not proof that every expected batch has arrived.

## Dataset scope

The report describes a Russo-Ukrainian War source collection of 57,384,192 tweets from 7,744,714 users, and a COVID-19 collection of 1,785,043,839 English tweets. It describes 775 hourly Ukraine network snapshots with up to approximately 45,000 nodes each. These are reported dataset characteristics; they are not verified counts of records successfully processed in one pipeline trial. The preview does not include sufficient raw measurements to reconstruct pipeline throughput, latency distributions, loss rates, or confidence intervals.

## Separate MPI results

The broader project's MPI experiments report modest speedup with 1-16 processes on email-Enron, comparable clustering fitness despite changing partitions, and advantages on larger networks in a 15-network comparison using four processes. Smaller networks incurred parallel overhead. The report also says the MPI implementation did not match the performance of PLM, PLP, and PSCAN. These results must not be relabelled as Kafka scaling measurements or solely attributed to this repository.

## Current source-review observations

At revision `108a4edc0bad38c4e130bd2906fe8eb31d7205f8`:

- `shell-scripts/runPipeline.sh` prints each script entry but never executes it in its final loop. Its success messages do not establish deployment success.
- `src/application/runapplication.sh` uses unchanged file counts across a wait interval to trigger clustering. This is a heuristic, not a completeness check; its surrounding loop is commented out.
- `src/merge/runmerge.sh` initializes `all_files_found=true` while the required-file checks are commented out. The request notification is also commented out.
- `src/producer/KafkaProducer.py` uses `acks=1`. That setting alone neither explains the historical missing-data observation nor proves downstream completion.

These are static observations. No historical runtime was redeployed and no new performance claims are made. Source files are preserved in this documentation update so historical behavior remains inspectable.
