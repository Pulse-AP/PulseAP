'''
StorageConsensus Module

This module handles the consensus logic around distributed storage validation.
It is NOT responsible for raw storage or file handling — those are part of the
Storage or Sector modules. Instead, StorageConsensus is responsible for coordinating
the rules and behaviors that ensure partners are storing data truthfully over time.

Key Responsibilities:
- Orchestrates and verifies challenge/response flows between partners.
- Interfaces with validators to issue deterministic, zero-value job-based challenges.
- Validates Merkle proofs (when escalated), including root matching and path validation.
- Tracks per-sector modification history tied to job file IDs and timestamps.
- Differentiates between mutable and immutable storage types.
- Assigns and enforces reputation score adjustments based on outcome of challenges.
- Delegates all final failure decisions to the validator after partner-vs-partner disputes.
- Abstracts sector size and supports future scaling (e.g., 4GB → 4TB).
- Avoids direct file access — expects partners to return signatures and hashes only.

Important Notes:
- All validator-issued challenges are formalized as job files with 0 MTR value.
- Partners must not challenge sectors they hold themselves.
- Challenge assignments are deterministic (seeded from the previous block hash).
- This module assumes all proofs and mutations are cryptographically signed.

This is a trust-minimized enforcement layer designed to ensure network-wide honesty
in a decentralized storage market. It prioritizes validator efficiency and scales
without central dependencies.
