"""Retrieval queries against the P94 promoted index format.

The promoted index is assembled from chunk manifests and P94 audit metadata.
Exposes two query functions:
- query_by_page_range(doc_id, start, end) -> Use Case 1 output
- trace_full_document(doc_id, group_by=None) -> Use Case 2 output
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _default_repo_root() -> Path:
    """Return the repo root. Tries __file__ first (editable install), falls back to cwd."""
    candidates = [
        Path(os.path.dirname(os.path.abspath(__file__))).parents[2],
        Path.cwd(),
    ]
    for p in candidates:
        if (p / 'pyproject.toml').exists():
            return p.resolve()
    return candidates[-1].resolve()


class IndexRecord:
    """A single promoted-index record (one chunk) loaded from a manifest."""

    __slots__ = [
        'document_id', 'source_hash', 'page_anchor_start', 'page_anchor_end',
        'chunk_id', 'model_lane', 'audit_status', 'is_dedup', 'runtime_text_path',
    ]

    def __init__(
        self,
        document_id: str,
        source_hash: str | None = None,
        page_anchor_start: int | None = None,
        page_anchor_end: int | None = None,
        chunk_id: str | None = None,
        model_lane: str | None = None,
        audit_status: str | None = None,
        is_dedup: bool = False,
        runtime_text_path: str | None = None,
    ):
        self.document_id = document_id
        self.source_hash = source_hash
        self.page_anchor_start = page_anchor_start
        self.page_anchor_end = page_anchor_end
        self.chunk_id = chunk_id
        self.model_lane = model_lane
        self.audit_status = audit_status
        self.is_dedup = is_dedup
        self.runtime_text_path = runtime_text_path

    def overlaps_page_range(self, start: int, end: int) -> bool:
        if self.page_anchor_start is None or self.page_anchor_end is None:
            return False
        return self.page_anchor_start <= end and self.page_anchor_end >= start

    def to_output_record(
        self,
        include_source_hashes: bool = True,
        include_model_lane: bool = True,
    ) -> dict[str, Any]:
        record: dict[str, Any] = {}
        if self.source_hash is not None and include_source_hashes:
            record['source_hash'] = self.source_hash
        record['document_id'] = self.document_id
        if self.page_anchor_start is not None and self.page_anchor_end is not None:
            record['page_anchor'] = (self.page_anchor_start + self.page_anchor_end) // 2
            record['page_range_start'] = self.page_anchor_start
            record['page_range_end'] = self.page_anchor_end
        if self.chunk_id is not None:
            record['chunk_id'] = self.chunk_id
        if self.model_lane is not None and include_model_lane:
            record['model_lane'] = self.model_lane
        if self.audit_status is not None:
            record['audit_status'] = self.audit_status
        if self.runtime_text_path is not None:
            record['text_file'] = self.runtime_text_path
        if self.is_dedup:
            record['is_dedup'] = True
        return record


class PromotedIndex:
    """Load and query the P94 promoted index from chunk manifests + audit metadata."""

    def __init__(
        self,
        repo_root: Path | None = None,
        corpus_dir: str = 'benchmarks/document_library/tsa23_tsr',
        manifest_glob: str = '*.json',
        p94_packet_path: str | None = None,
    ):
        self.repo_root = repo_root or _default_repo_root()
        self.corpus_dir = self.repo_root / corpus_dir
        self.p94_packet_path = (
            Path(p94_packet_path)
            if p94_packet_path
            else self.repo_root / 'benchmarks/document_library/p94_project_owned_index_decision_packet.json'
        )
        self.documents: dict[str, list[IndexRecord]] = {}
        self.model_lane: str = 'unknown'
        self._load_manifests(manifest_glob)
        self._load_audit_metadata()

    def _load_manifests(self, glob_pattern: str) -> None:
        manifest_dir = self.corpus_dir / 'chunk_manifests'
        if not manifest_dir.is_dir():
            return
        for mf_path in sorted(manifest_dir.glob(glob_pattern)):
            with open(mf_path, 'r') as f:
                manifest = json.load(f)
            doc_id = Path(mf_path.name).stem
            records: list[IndexRecord] = []
            for chunk in manifest.get('chunks', []):
                rec = IndexRecord(
                    document_id=doc_id,
                    source_hash=chunk.get('text_sha256'),
                    page_anchor_start=chunk.get('page_start'),
                    page_anchor_end=chunk.get('page_end'),
                    chunk_id=chunk.get('chunk_id'),
                    runtime_text_path=chunk.get('runtime_text_path'),
                )
                records.append(rec)
            if records:
                self.documents[doc_id] = sorted(records, key=lambda r: (r.page_anchor_start or 0))

    def _load_audit_metadata(self) -> None:
        if not self.p94_packet_path.is_file():
            return
        with open(self.p94_packet_path, 'r') as f:
            packet = json.load(f)
        quality = packet.get('quality_outcome', {})
        self.model_lane = quality.get('model_lane', 'unknown')
        records_by_doc = quality.get('records_by_document', {})
        for doc_id, recs in self.documents.items():
            info = records_by_doc.get(doc_id, {})
            count = info.get('count', 0)
            dedup_flagged = info.get('dedup_flagged', 0)
            for rec in recs:
                rec.model_lane = self.model_lane
            if dedup_flagged > 0 and count == dedup_flagged:
                for rec in recs:
                    rec.audit_status = 'accepted_pending_dedup'
                    rec.is_dedup = True
            elif count > 0 and dedup_flagged == 0:
                for rec in recs:
                    rec.audit_status = 'accepted'
                    rec.is_dedup = False

    @property
    def all_document_ids(self) -> list[str]:
        return sorted(self.documents.keys())

    @property
    def total_record_count(self) -> int:
        return sum(len(recs) for recs in self.documents.values())


def query_by_page_range(
    doc_id: str,
    start: int,
    end: int,
    index: PromotedIndex | None = None,
    include_source_hashes: bool = True,
    include_model_lane: bool = True,
) -> dict[str, Any]:
    """Use Case 1 - Page/Chunk Anchor Lookup."""
    if index is None:
        index = PromotedIndex()
    records = index.documents.get(doc_id)
    if not records:
        return {
            'query': {'document_id': doc_id, 'page_range': {'start': start, 'end': end}},
            'flat_array': [],
            'metadata': {'total_record_count': 0, 'group_by': 'none',
                         'returned_at': datetime.now(timezone.utc).isoformat()},
        }
    filtered = sorted(
        [r for r in records if r.overlaps_page_range(start, end)],
        key=lambda r: (r.page_anchor_start or 0),
    )
    output = [r.to_output_record(include_source_hashes, include_model_lane) for r in filtered]
    return {
        'query': {'document_id': doc_id, 'page_range': {'start': start, 'end': end}},
        'flat_array': output,
        'metadata': {'total_record_count': len(output), 'group_by': 'none',
                     'returned_at': datetime.now(timezone.utc).isoformat()},
    }


def trace_full_document(
    doc_id: str,
    group_by: str = 'none',
    index: PromotedIndex | None = None,
) -> dict[str, Any]:
    """Use Case 2 - Full-Document Provenance Trace."""
    if index is None:
        index = PromotedIndex()
    records = index.documents.get(doc_id)
    if not records:
        return {'flat_array': [], 'metadata': {'document_id': doc_id, 'total_record_count': 0}}
    output = [r.to_output_record() for r in records]
    result: dict[str, Any] = {}
    if group_by == 'audit_status':
        grouped: dict[str, list[dict]] = {}
        for rec in output:
            grouped.setdefault(rec.get('audit_status', 'unknown'), []).append(rec)
        result['grouped_by_audit_status'] = grouped
    elif group_by == 'model_lane':
        grouped: dict[str, list[dict]] = {}
        for rec in output:
            grouped.setdefault(rec.get('model_lane', 'unknown'), []).append(rec)
        result['grouped_by_model_lane'] = grouped
    result['flat_array'] = output
    result['metadata'] = {
        'document_id': doc_id,
        'total_record_count': len(output),
        'group_by': group_by,
        'returned_at': datetime.now(timezone.utc).isoformat(),
    }
    return result
