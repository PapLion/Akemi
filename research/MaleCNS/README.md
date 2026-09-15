# MaleCNS v1.0 — adult male Drosophila connectome

This folder tracks the canonical **MaleCNS v1.0** connectome resource for the adult male *Drosophila melanogaster* central nervous system.

## What this is

- Complete male CNS connectome: brain, optic lobes, cervical connective and ventral nerve cord.
- Published dataset: ~166.7k neurons and ~125M synaptic connections.
- Canonical interactive/download site: https://male-cns.janelia.org/
- Official download page: https://male-cns.janelia.org/download/
- neuPrint dataset: `male-cns:v1.0`
- Dataset license: CC BY.

## Primary paper

Berg S, Beckett IR, Costa M, Schlegel P, et al. **Sexual dimorphism in the complete Drosophila male central nervous system connectome.** *Cell*. 2026 Sep 03;189(18):5504-5526.e15. DOI: `10.1016/j.cell.2026.08.015`.

## Official supplemental repository

The submodule at `upstream-2025malecns/` points to:

- https://github.com/flyconnectome/2025malecns
- pinned commit: `67767d2233657983993ff6c2be48e836a935863c`

That GitHub repository contains supplemental/derived products for the paper. The **primary connectome artifacts are not all stored in GitHub**; they are published separately through the MaleCNS download infrastructure because several files are gigabytes to many gigabytes in size.

Initialize it after cloning Akemi:

```bash
git submodule update --init --recursive research/MaleCNS/upstream-2025malecns
```

## Primary v1.0 data

Public bucket root:

```text
gs://flyem-male-cns/v1.0/
```

Flat-connectome directory:

```text
gs://flyem-male-cns/v1.0/connectome-data/flat-connectome/
```

Key files include:

- `connectome-weights-male-cns-v1.0-minconf-0.5.feather` — full segment-to-segment connection graph (~1.1 GB).
- `body-annotations-male-cns-v1.0-minconf-0.5.feather` — curated neuron annotations (~13 MB).
- `body-neurotransmitters-male-cns-v1.0.feather` — aggregate neurotransmitter predictions (~42 MB).
- `body-stats-male-cns-v1.0-minconf-0.5.feather` — segment/synapse summary statistics (~780 MB).
- `syn-points-male-cns-v1.0-minconf-0.5.feather` — synapse locations (~12.7 GB).
- `syn-partners-male-cns-v1.0-minconf-0.5.feather` — pre/post partner pairs (~6.8 GB).

Skeletons for all neurons are also available under the v1.0 segmentation tree, including SWC exports.

## Public announcement / context

Google Research overview:

- https://research.google/blog/a-connectomics-milestone-mapping-the-complete-male-fruit-fly-brain/

Google AI community thread referenced during the September 2026 wave of connectome experiments:

- https://x.com/GoogleAI/status/2098109357624095155

Video that triggered this import into Akemi:

- https://youtu.be/KOwsVDogscY

## Why this is a submodule

The upstream scientific repo is hundreds of megabytes and the primary MaleCNS dataset is much larger still. Vendoring copies into Akemi would duplicate history and make provenance/update tracking worse. A pinned submodule keeps the exact scientific source reproducible while this folder documents the canonical external dataset that future Akemi experiments should consume.
