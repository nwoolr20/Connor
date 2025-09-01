"""
Pattern Recognition Module for Connor System
Provides pattern recognition capabilities for memory and learning systems
"""

from typing import Dict, List, Any, Optional, Tuple
import re
from collections import defaultdict


class PatternRecognizer:
    """Pattern recognition system for memory and behavioral analysis"""
    
    def __init__(self):
        self.patterns = {}
        self.pattern_counts = defaultdict(int)
        self.sequence_patterns = []
    
    def learn_pattern(self, pattern_id: str, data: Any, context: Optional[Dict[str, Any]] = None):
        """Learn a new pattern from data"""
        self.patterns[pattern_id] = {
            "data": data,
            "context": context or {},
            "frequency": 1,
            "confidence": 0.5
        }
        self.pattern_counts[pattern_id] += 1
    
    def recognize_patterns(self, input_data: Any) -> List[Dict[str, Any]]:
        """Recognize patterns in input data"""
        recognized = []
        
        for pattern_id, pattern_info in self.patterns.items():
            similarity = self._calculate_similarity(input_data, pattern_info["data"])
            if similarity > 0.7:  # Threshold for pattern recognition
                recognized.append({
                    "pattern_id": pattern_id,
                    "similarity": similarity,
                    "confidence": pattern_info["confidence"],
                    "context": pattern_info["context"]
                })
        
        return sorted(recognized, key=lambda x: x["similarity"], reverse=True)
    
    def _calculate_similarity(self, data1: Any, data2: Any) -> float:
        """Calculate similarity between two data points"""
        if isinstance(data1, str) and isinstance(data2, str):
            # Simple string similarity
            common_words = set(data1.lower().split()) & set(data2.lower().split())
            total_words = set(data1.lower().split()) | set(data2.lower().split())
            return len(common_words) / max(len(total_words), 1)
        elif isinstance(data1, (int, float)) and isinstance(data2, (int, float)):
            # Numerical similarity
            return 1.0 - abs(data1 - data2) / max(abs(data1), abs(data2), 1)
        else:
            # Generic similarity
            return 0.5 if str(data1) == str(data2) else 0.1
    
    def analyze_sequence_patterns(self, sequence: List[Any]) -> List[Dict[str, Any]]:
        """Analyze patterns in sequences"""
        patterns = []
        
        # Look for repeating subsequences
        for length in range(2, min(len(sequence) // 2 + 1, 5)):
            for start in range(len(sequence) - length + 1):
                subseq = sequence[start:start + length]
                occurrences = self._find_subsequence_occurrences(sequence, subseq)
                if len(occurrences) > 1:
                    patterns.append({
                        "pattern": subseq,
                        "length": length,
                        "occurrences": occurrences,
                        "frequency": len(occurrences)
                    })
        
        return sorted(patterns, key=lambda x: x["frequency"], reverse=True)
    
    def _find_subsequence_occurrences(self, sequence: List[Any], subseq: List[Any]) -> List[int]:
        """Find all occurrences of a subsequence in a sequence"""
        occurrences = []
        for i in range(len(sequence) - len(subseq) + 1):
            if sequence[i:i + len(subseq)] == subseq:
                occurrences.append(i)
        return occurrences
    
    def get_pattern_statistics(self) -> Dict[str, Any]:
        """Get statistics about learned patterns"""
        return {
            "total_patterns": len(self.patterns),
            "pattern_counts": dict(self.pattern_counts),
            "average_confidence": sum(p["confidence"] for p in self.patterns.values()) / max(len(self.patterns), 1)
        }