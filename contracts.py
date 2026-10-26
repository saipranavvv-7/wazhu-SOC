from dataclasses import dataclass, field


@dataclass
class Chunk:
    id: str
    source_type: str  # "mitre" | "nist" | "ir"
    title: str
    text: str
    tags: list[str] = field(default_factory=list)
