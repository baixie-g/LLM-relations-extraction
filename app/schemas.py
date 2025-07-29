from pydantic import BaseModel, Field
from typing import List, Dict, Any
from typing_extensions import Literal

class SchemaItem(BaseModel):
    schema_name: str = Field(..., alias="schema", description="Schema name such as 'crime' or 'flights'")
    triplet: List[str] = Field(..., description="List of allowed triplets in the format 'Entity-Relation->Target'")

class ExtractionRequest(BaseModel):
    text: str = Field(..., description="The input text to extract knowledge graph from")
    schema_info: SchemaItem = Field(..., alias="schema", description="Schema information containing allowed entities and relations")

class Node(BaseModel):
    id: str = Field(..., description="Unique identifier for the node, formatted as type_number")
    name: str = Field(..., description="Name of the entity")
    type: str = Field(..., description="Type of the entity, e.g., Person, Organization")
    aliases: List[str] = Field(default_factory=list, description="List of alternative names or aliases")
    definition: str = Field("", description="A brief definition or description of the entity")
    attributes: Dict[str, List[Any]] = Field(default_factory=dict, description="Attributes of the entity, key-value pairs where values are arrays")

class Relationship(BaseModel):
    source: str = Field(..., description="Source entity ID")
    target: str = Field(..., description="Target entity ID")
    type: str = Field(..., description="Type of the relationship")

class ExtractionResponse(BaseModel):
    nodes: List[Node] = Field(..., description="List of extracted nodes")
    relationships: List[Relationship] = Field(..., description="List of extracted relationships")