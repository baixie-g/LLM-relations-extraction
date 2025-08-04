import json
import re
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from app.schemas import PromptEvaluationRequest, PromptEvaluationResponse
from app.kg_extractor import LLMKGExtractor


@dataclass
class EvaluationMetrics:
    """评估指标"""
    completeness: float = 0.0  # 完整性
    accuracy: float = 0.0      # 准确性
    consistency: float = 0.0   # 一致性
    relevance: float = 0.0     # 相关性


class PromptEvaluator:
    def __init__(self):
        """初始化提示词评估器"""
        self.kg_extractor = LLMKGExtractor()

    def evaluate_template(
        self, 
        template_id: str,
        template_name: str,
        template_content: str,
        test_texts: List[str],
        schema_info,
        evaluation_metrics: List[str]
    ) -> PromptEvaluationResponse:
        """
        评估提示词模板
        """
        detailed_results = []
        total_scores = {metric: 0.0 for metric in evaluation_metrics}
        
        for i, text in enumerate(test_texts):
            try:
                # 渲染提示词
                from app.prompt_manager import EnhancedPromptManager
                temp_manager = EnhancedPromptManager()
                
                # 临时设置模板内容
                temp_template = temp_manager.get_active_template("zh")
                if temp_template:
                    temp_template.content = template_content
                
                prompt = temp_manager.render_prompt("zh", text, schema_info)
                
                # 执行抽取
                result = self.kg_extractor.extract(prompt)
                
                # 评估结果
                scores = self._evaluate_single_result(
                    result, text, schema_info, evaluation_metrics
                )
                
                detailed_results.append({
                    "test_index": i,
                    "text": text[:100] + "..." if len(text) > 100 else text,
                    "extraction_result": result,
                    "scores": scores
                })
                
                # 累加分数
                for metric in evaluation_metrics:
                    if metric in scores:
                        total_scores[metric] += scores[metric]
                        
            except Exception as e:
                detailed_results.append({
                    "test_index": i,
                    "text": text[:100] + "..." if len(text) > 100 else text,
                    "error": str(e),
                    "scores": {metric: 0.0 for metric in evaluation_metrics}
                })
        
        # 计算平均分数
        num_tests = len(test_texts)
        evaluation_results = {
            metric: total_scores[metric] / num_tests if num_tests > 0 else 0.0
            for metric in evaluation_metrics
        }
        
        # 生成评估总结
        summary = self._generate_evaluation_summary(
            template_name, evaluation_results, detailed_results
        )
        
        return PromptEvaluationResponse(
            template_id=template_id,
            template_name=template_name,
            evaluation_results=evaluation_results,
            detailed_results=detailed_results,
            summary=summary
        )

    def _evaluate_single_result(
        self, 
        result: Dict[str, Any], 
        text: str, 
        schema_info,
        metrics: List[str]
    ) -> Dict[str, float]:
        """评估单个抽取结果"""
        scores = {}
        
        if "completeness" in metrics:
            scores["completeness"] = self._calculate_completeness(result, text, schema_info)
        
        if "accuracy" in metrics:
            scores["accuracy"] = self._calculate_accuracy(result, text, schema_info)
        
        if "consistency" in metrics:
            scores["consistency"] = self._calculate_consistency(result)
        
        if "relevance" in metrics:
            scores["relevance"] = self._calculate_relevance(result, text)
        
        return scores

    def _calculate_completeness(self, result: Dict[str, Any], text: str, schema_info) -> float:
        """计算完整性分数"""
        try:
            nodes = result.get("nodes", [])
            relationships = result.get("relationships", [])
            
            # 检查是否提取了节点和关系
            if not nodes and not relationships:
                return 0.0
            
            # 计算文本中可能存在的实体数量（简单估算）
            # 这里可以根据具体需求调整算法
            text_entities = self._estimate_entities_in_text(text, schema_info)
            
            if text_entities == 0:
                return 1.0 if nodes else 0.0
            
            # 计算提取的实体覆盖率
            extracted_entities = len(nodes)
            coverage = min(extracted_entities / text_entities, 1.0)
            
            # 考虑关系提取
            relationship_bonus = min(len(relationships) / max(len(nodes), 1), 0.3)
            
            return min(coverage + relationship_bonus, 1.0)
            
        except Exception:
            return 0.0

    def _calculate_accuracy(self, result: Dict[str, Any], text: str, schema_info) -> float:
        """计算准确性分数"""
        try:
            nodes = result.get("nodes", [])
            relationships = result.get("relationships", [])
            
            if not nodes and not relationships:
                return 0.0
            
            accuracy_scores = []
            
            # 检查节点准确性
            for node in nodes:
                node_score = self._check_node_accuracy(node, text, schema_info)
                accuracy_scores.append(node_score)
            
            # 检查关系准确性
            for rel in relationships:
                rel_score = self._check_relationship_accuracy(rel, nodes, text, schema_info)
                accuracy_scores.append(rel_score)
            
            return sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0.0
            
        except Exception:
            return 0.0

    def _calculate_consistency(self, result: Dict[str, Any]) -> float:
        """计算一致性分数"""
        try:
            nodes = result.get("nodes", [])
            relationships = result.get("relationships", [])
            
            if not nodes:
                return 0.0
            
            consistency_scores = []
            
            # 检查ID格式一致性
            id_pattern = re.compile(r'^[a-zA-Z_]+_\d+$')
            id_consistency = sum(1 for node in nodes if id_pattern.match(node.get("id", ""))) / len(nodes)
            consistency_scores.append(id_consistency)
            
            # 检查类型一致性
            types = [node.get("type", "") for node in nodes]
            type_consistency = len(set(types)) / len(types) if types else 0.0
            consistency_scores.append(type_consistency)
            
            # 检查关系引用一致性
            if relationships and nodes:
                node_ids = {node.get("id", "") for node in nodes}
                valid_refs = sum(1 for rel in relationships 
                               if rel.get("source", "") in node_ids and rel.get("target", "") in node_ids)
                ref_consistency = valid_refs / len(relationships) if relationships else 1.0
                consistency_scores.append(ref_consistency)
            
            return sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0.0
            
        except Exception:
            return 0.0

    def _calculate_relevance(self, result: Dict[str, Any], text: str) -> float:
        """计算相关性分数"""
        try:
            nodes = result.get("nodes", [])
            
            if not nodes:
                return 0.0
            
            relevance_scores = []
            
            for node in nodes:
                name = node.get("name", "")
                if name:
                    # 检查实体名称是否在文本中出现
                    if name.lower() in text.lower():
                        relevance_scores.append(1.0)
                    else:
                        # 检查部分匹配
                        partial_match = any(word in text.lower() for word in name.lower().split())
                        relevance_scores.append(0.5 if partial_match else 0.0)
                else:
                    relevance_scores.append(0.0)
            
            return sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
            
        except Exception:
            return 0.0

    def _estimate_entities_in_text(self, text: str, schema_info) -> int:
        """估算文本中可能存在的实体数量"""
        # 简单的实体数量估算
        # 可以根据具体需求使用更复杂的NLP方法
        words = text.split()
        return max(len(words) // 20, 1)  # 假设每20个词包含一个实体

    def _check_node_accuracy(self, node: Dict[str, Any], text: str, schema_info) -> float:
        """检查节点准确性"""
        score = 0.0
        
        # 检查必要字段
        if node.get("id") and node.get("name") and node.get("type"):
            score += 0.3
        
        # 检查名称是否在文本中
        name = node.get("name", "")
        if name and name.lower() in text.lower():
            score += 0.4
        
        # 检查类型是否在允许的类型中
        node_type = node.get("type", "")
        allowed_types = self._extract_allowed_types(schema_info)
        if node_type in allowed_types:
            score += 0.3
        
        return score

    def _check_relationship_accuracy(self, rel: Dict[str, Any], nodes: List[Dict], text: str, schema_info) -> float:
        """检查关系准确性"""
        score = 0.0
        
        # 检查必要字段
        if rel.get("source") and rel.get("target") and rel.get("type"):
            score += 0.4
        
        # 检查源和目标节点是否存在
        node_ids = {node.get("id", "") for node in nodes}
        if rel.get("source", "") in node_ids and rel.get("target", "") in node_ids:
            score += 0.3
        
        # 检查关系类型是否在允许的类型中
        rel_type = rel.get("type", "")
        allowed_relations = self._extract_allowed_relations(schema_info)
        if rel_type in allowed_relations:
            score += 0.3
        
        return score

    def _extract_allowed_types(self, schema_info) -> List[str]:
        """提取允许的实体类型"""
        allowed_types = set()
        for triplet in schema_info.triplet:
            parts = triplet.split('-')
            if len(parts) >= 2:
                allowed_types.add(parts[0])
                if '->' in triplet:
                    target_part = triplet.split('->')[1]
                    allowed_types.add(target_part)
        return list(allowed_types)

    def _extract_allowed_relations(self, schema_info) -> List[str]:
        """提取允许的关系类型"""
        allowed_relations = set()
        for triplet in schema_info.triplet:
            if '->' in triplet:
                relation_part = triplet.split('->')[0].split('-', 1)[1]
                allowed_relations.add(relation_part)
        return list(allowed_relations)

    def _generate_evaluation_summary(
        self, 
        template_name: str, 
        evaluation_results: Dict[str, float], 
        detailed_results: List[Dict[str, Any]]
    ) -> str:
        """生成评估总结"""
        summary_parts = [f"模板 '{template_name}' 的评估结果："]
        
        # 添加各项指标分数
        for metric, score in evaluation_results.items():
            summary_parts.append(f"- {metric}: {score:.2f}")
        
        # 添加统计信息
        successful_tests = sum(1 for result in detailed_results if "error" not in result)
        total_tests = len(detailed_results)
        success_rate = successful_tests / total_tests if total_tests > 0 else 0.0
        
        summary_parts.append(f"- 成功率: {success_rate:.2f} ({successful_tests}/{total_tests})")
        
        # 添加建议
        avg_score = sum(evaluation_results.values()) / len(evaluation_results) if evaluation_results else 0.0
        if avg_score >= 0.8:
            summary_parts.append("建议: 模板效果优秀，可以继续使用")
        elif avg_score >= 0.6:
            summary_parts.append("建议: 模板效果良好，可以考虑小幅优化")
        elif avg_score >= 0.4:
            summary_parts.append("建议: 模板效果一般，需要进一步优化")
        else:
            summary_parts.append("建议: 模板效果较差，建议重新设计")
        
        return "\n".join(summary_parts) 