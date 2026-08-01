# GenModule design

## Source basis

The workflow distills the read-only design note
`${BIOWORKSPACE_ROOT}/Zhixins-KB/5.Archive/ChatGPT/2026-GPT-AI抗体合成.md`,
section `指定表位的 de novo antibody design`. The source's target, antigen,
epitope, IP/FTO, structure, de novo design, computational, experimental,
affinity-maturation, ADC, patent, negative-design, and asset-diversity concepts
are preserved as separately auditable stages. Implementation adds explicit
input/output contracts and refuses to invent sequences or validation evidence.

## Boundary

This module generates epitope-conditioned discovery candidates and evidence
packages. Target, Product, and Commercial/FTO Gates independently evaluate
whether those packages are sufficient.

## Frozen input

`EpitopeConditionedDiscoveryInput@0.1.0` contains:

- discovery and asset identifiers;
- target gene, protein, indication, sequence/accession, and provenance;
- antigen construct definition;
- one user-defined epitope with residue positions or explicit unresolved
  description;
- preferred antibody format and species/framework policy;
- positive objectives and negative constraints;
- ADC requirements;
- known biology, competitor antibodies, structures, and patent evidence.

## Frozen output

`EpitopeConditionedAntibodyAssetPackage@0.1.0` contains:

- target/antigen/epitope audit;
- epitope and IP/FTO search plan;
- design-ready structure requirements;
- positive and negative design constraints;
- generated candidate-family manifest, when an external adapter is configured;
- Pareto and family-diversity analysis;
- focused wet-lab and structural-validation plans;
- affinity-maturation eligibility;
- ADC-readiness gaps;
- patent package outline and final asset report.

## Critical rules

- No antibody sequence is generated without a configured, versioned external
  design adapter.
- Epitope residue numbering must be bound to one antigen construct and sequence
  version.
- Predicted binding pose is not epitope validation.
- Affinity maturation is disabled until experimental target binding and
  epitope evidence exist.
- The desired output is multiple independent asset families, not a top-N list.
- Legal FTO, patentability, safety, efficacy, and ADC-readiness claims remain
  outside the built-in module.
