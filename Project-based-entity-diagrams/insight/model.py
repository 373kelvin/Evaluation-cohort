"""Data model for an analyzed project (stdlib only)."""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Column:
    name: str
    type: str = ""
    pk: bool = False
    fk_to: Optional[str] = None      # "table.column"
    notes: str = ""
    inferred: bool = False


@dataclass
class Table:
    name: str
    columns: List[Column] = field(default_factory=list)
    source: str = ""                 # file:line
    inferred: bool = False           # True if recovered from queries, no DDL

    @property
    def pk_cols(self):
        return [c.name for c in self.columns if c.pk]


@dataclass
class Relationship:
    parent: str                      # table
    child: str                       # table
    key: str                         # join key description
    source: str = ""
    inferred: bool = False


@dataclass
class Feature:
    name: str                        # short title (route/handler)
    role: str = "general"            # auth / student / admin / public / general
    detail: str = ""                 # what it does + side effects
    source: str = ""                 # file:line
    http: str = ""                   # GET/POST if known
    ops: list = field(default_factory=list)   # SQL ops this feature performs


@dataclass
class Project:
    name: str = "Project"
    languages: List[str] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)
    verdict: str = ""                # one-line classification
    how_to_run: List[str] = field(default_factory=list)   # (command, source)
    entry_points: List[str] = field(default_factory=list)
    data_layer: str = ""
    db_name: str = ""
    tables: List[Table] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)
    features: List[Feature] = field(default_factory=list)
    findings: List[str] = field(default_factory=list)     # smells / notes
    file_count: int = 0
    has_ddl: bool = False
    # --- software-design views (auto-derived) ---
    architecture: str = ""           # Mermaid flowchart of components
    exec_title: str = ""             # name of the flow shown
    exec_map: str = ""               # Mermaid sequenceDiagram
    components: list = field(default_factory=list)  # (name, role, file_count)
