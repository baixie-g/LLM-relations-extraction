import re
import logging
from typing import List, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_id(entity_type: str, index: int) -> str:
    """
    生成唯一实体 ID，格式为 type_index，例如 person_001
    """
    return f"{entity_type.lower()}_{index:03d}"


def extract_entity_type_from_triplet(triplet: str) -> Optional[str]:
    """
    从 triplet 中提取实体类型，例如 "Person-HAS_PHONE->Phone" → "Person"
    """
    match = re.match(r"([A-Za-z0-9_]+)-", triplet)
    if match:
        return match.group(1)
    return None


def extract_relation_type(triplet: str) -> Optional[str]:
    """
    从 triplet 中提取关系类型，例如 "Person-HAS_PHONE->Phone" → "HAS_PHONE"
    """
    match = re.search(r"-([A-Za-z0-9_]+)->", triplet)
    if match:
        return match.group(1)
    return None


def extract_target_type(triplet: str) -> Optional[str]:
    """
    从 triplet 中提取目标类型，例如 "Person-HAS_PHONE->Phone" → "Phone"
    """
    match = re.search(r"->([A-Za-z0-9_]+)", triplet)
    if match:
        return match.group(1)
    return None


def get_allowed_node_types(schema_triplets: List[str]) -> List[str]:
    """
    从 schema 的 triplet 中提取所有允许的节点类型
    """
    node_types = set()
    for triplet in schema_triplets:
        src = extract_entity_type_from_triplet(triplet)
        tgt = extract_target_type(triplet)
        if src:
            node_types.add(src)
        if tgt:
            node_types.add(tgt)
    return sorted(list(node_types))


def get_allowed_relations(schema_triplets: List[str]) -> List[str]:
    """
    从 schema 的 triplet 中提取所有允许的关系类型
    """
    relations = set()
    for triplet in schema_triplets:
        rel = extract_relation_type(triplet)
        if rel:
            relations.add(rel)
    return sorted(list(relations))


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    快速创建 logger 实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger


if __name__ == "__main__":
    # 示例测试
    triplet = "Person-HAS_PHONE->Phone"
    print("Entity Type:", extract_entity_type_from_triplet(triplet))
    print("Relation Type:", extract_relation_type(triplet))
    print("Target Type:", extract_target_type(triplet))