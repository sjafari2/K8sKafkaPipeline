# K8sKafkaPipeline: streaming graph analysis with PASCAL-G

A historical University of New Mexico research pipeline connecting text ingestion, Kafka, sparse graph construction, local PASCAL-G clustering, and cluster merging on Kubernetes/Nautilus.

## Project provenance

Recorded Git development begins in September 2023. The existing `v1.0` tag points to the February 2, 2024 revision. The supplied NSF award 1807563 final annual report preview names this repository and lists its 2024 software/data product under NSF-PAR record **10489782**. See [project history and evidence](docs/Project-history.md) for dates, contributors, and source qualifications.

This September 2026 documentation update preserves the historical source and Git history. It adds an evidence-based account of the project; it does not claim new benchmark results.

## Read the project

- [Architecture and data flow](docs/Architecture-and-data-flow.md)
- [Reported findings and limitations](docs/Findings-and-limitations.md)
- [Reproduction and next steps](docs/Reproduction-and-next-steps.md)
- [Project history and contributors](docs/Project-history.md)
- [Historical README](docs/Historical-README.md)
- [Wiki source pages](docs/wiki/Home.md)

## Implementation status

The source contains the request, producer, consumer, application, and merge stages, with deployment and image-building files. Static review found that the top-level launcher only prints its script entries, and some completeness/notification checks are inactive. Read the reproduction notes before running. No deployment or runtime validation was performed for this documentation update.

The NSF report describes missing-data and clustering-quality challenges and proposes further sequence-tagging work. It does not establish a loss-free or exactly-once pipeline. MPI benchmark findings in the broader report concern separate algorithm work and are not Kafka scaling measurements.

## Contributors

The historical project credits Soheila Jafari Khouzani, Nidia Vaquera Chavez, Patrick Bridges, and Trilce Estrada. The [history page](docs/Project-history.md) distinguishes individual role evidence from collaborative outcomes.
