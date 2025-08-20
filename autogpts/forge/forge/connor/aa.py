"""
Apprentice Agent (AA)

Apprentice Agents are assigned to families producing more than two children,
facilitating faster information access. They specialize in information retrieval
and family assistance within the learning agent ecosystem.
"""

from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass
import time
from .base import BaseConnorAgent, AgentMessage, AgentType, AgentConfig
from forge.sdk import ForgeLogger

LOG = ForgeLogger(__name__)


@dataclass
class FamilyArchive:
    """Represents archived information from a learning agent family."""
    family_id: str
    archived_members: List[str]
    knowledge_index: Dict[str, List[str]]  # topic -> relevant archived agents
    access_patterns: Dict[str, int]  # agent_id -> access_count
    creation_time: float = None
    
    def __post_init__(self):
        if self.creation_time is None:
            self.creation_time = time.time()


@dataclass
class InformationRequest:
    """Represents a request for information retrieval."""
    request_id: str
    requester_id: str
    query: str
    priority: int = 1
    deadline: Optional[float] = None
    context: Dict[str, Any] = None
    status: str = "pending"  # pending, processing, completed, failed
    result: Optional[Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}


@dataclass
class CacheEntry:
    """Represents a cached piece of information."""
    cache_id: str
    query: str
    result: Any
    source_agent: str
    access_count: int = 0
    last_accessed: float = None
    expiry_time: Optional[float] = None
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = time.time()


class ApprenticeAgent(BaseConnorAgent):
    """
    Apprentice Agent that facilitates information access and family coordination.
    
    AAs are created when learning agent families produce more than two children,
    and they provide efficient access to archived knowledge and family coordination.
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.family_id = config.family_id
        self.parent_id = config.parent_id
        self.sibling_apprentices = set()  # Other AAs in the same family
        self.family_archives = {}  # family_id -> FamilyArchive
        self.information_cache = {}  # query_hash -> CacheEntry
        self.request_queue = []
        self.access_statistics = {}
        self.communication_protocols = self._initialize_protocols()
        
    def _initialize_protocols(self) -> Dict[str, Any]:
        """Initialize communication protocols for family coordination."""
        return {
            "cache_sync_interval": 300,  # 5 minutes
            "archive_rotation_interval": 3600,  # 1 hour
            "priority_thresholds": {
                "urgent": 1,
                "high": 2,
                "normal": 3,
                "low": 4
            },
            "max_cache_size": 1000,
            "cache_ttl": 1800  # 30 minutes
        }
    
    async def process_input(self, input_data: Any) -> Dict[str, Any]:
        """
        Process input as an information retrieval and coordination request.
        
        Args:
            input_data: Information request or coordination task
            
        Returns:
            Response with retrieved information or coordination results
        """
        # Determine request type
        if isinstance(input_data, dict):
            request_type = input_data.get("type", "information_request")
            query = input_data.get("query", input_data.get("original_input", ""))
            requester_id = input_data.get("requester_id", "unknown")
            priority = input_data.get("priority", 3)
        else:
            request_type = "information_request"
            query = str(input_data)
            requester_id = "unknown"
            priority = 3
        
        if request_type == "information_request":
            response = await self._handle_information_request(query, requester_id, priority)
        elif request_type == "family_coordination":
            response = await self._handle_family_coordination(input_data)
        elif request_type == "cache_management":
            response = await self._handle_cache_management(input_data)
        elif request_type == "archive_access":
            response = await self._handle_archive_access(input_data)
        else:
            response = await self._handle_general_request(input_data)
        
        # Update access statistics
        self._update_access_statistics(request_type, requester_id)
        
        # Add to memory
        self.add_to_memory({
            "request_type": request_type,
            "query": query[:100],  # Truncate long queries
            "requester_id": requester_id,
            "success": response.get("success", True),
            "timestamp": time.time()
        })
        
        return response
    
    async def _handle_information_request(self, query: str, requester_id: str, priority: int) -> Dict[str, Any]:
        """Handle information retrieval requests."""
        request_id = f"req_{int(time.time())}_{len(self.request_queue)}"
        
        # Create request object
        request = InformationRequest(
            request_id=request_id,
            requester_id=requester_id,
            query=query,
            priority=priority
        )
        
        # Check cache first
        cache_result = self._check_cache(query)
        if cache_result:
            LOG.info(f"AA {self.agent_id} served request from cache: {query[:50]}...")
            return {
                "request_id": request_id,
                "query": query,
                "result": cache_result.result,
                "source": "cache",
                "cache_hit": True,
                "processed_by": self.agent_id,
                "agent_type": self.agent_type.value,
                "success": True,
                "response_time": 0.1  # Very fast cache response
            }
        
        # Search family archives
        archive_result = await self._search_family_archives(query)
        if archive_result:
            # Cache the result
            self._add_to_cache(query, archive_result, "family_archive")
            
            LOG.info(f"AA {self.agent_id} served request from family archive: {query[:50]}...")
            return {
                "request_id": request_id,
                "query": query,
                "result": archive_result,
                "source": "family_archive",
                "cache_hit": False,
                "processed_by": self.agent_id,
                "agent_type": self.agent_type.value,
                "success": True,
                "response_time": 0.5
            }
        
        # Coordinate with sibling apprentices
        sibling_result = await self._coordinate_with_siblings(query, request)
        if sibling_result:
            # Cache the result
            self._add_to_cache(query, sibling_result, "sibling_coordination")
            
            LOG.info(f"AA {self.agent_id} served request through sibling coordination: {query[:50]}...")
            return {
                "request_id": request_id,
                "query": query,
                "result": sibling_result,
                "source": "sibling_coordination",
                "cache_hit": False,
                "processed_by": self.agent_id,
                "agent_type": self.agent_type.value,
                "success": True,
                "response_time": 1.0
            }
        
        # If no direct information found, provide guidance
        guidance = self._generate_guidance(query, request)
        
        return {
            "request_id": request_id,
            "query": query,
            "result": guidance,
            "source": "guidance_generation",
            "cache_hit": False,
            "processed_by": self.agent_id,
            "agent_type": self.agent_type.value,
            "success": False,
            "response_time": 0.3,
            "guidance_provided": True
        }
    
    def _check_cache(self, query: str) -> Optional[CacheEntry]:
        """Check if query result is available in cache."""
        query_hash = self._hash_query(query)
        
        if query_hash in self.information_cache:
            entry = self.information_cache[query_hash]
            
            # Check if cache entry is still valid
            if entry.expiry_time and time.time() > entry.expiry_time:
                del self.information_cache[query_hash]
                return None
            
            # Update access statistics
            entry.access_count += 1
            entry.last_accessed = time.time()
            
            return entry
        
        return None
    
    def _hash_query(self, query: str) -> str:
        """Create a hash for the query for caching purposes."""
        # Simple hash based on normalized query
        normalized = query.lower().strip()
        return str(hash(normalized) % 10000000)  # Keep it simple
    
    async def _search_family_archives(self, query: str) -> Optional[Any]:
        """Search through family archives for relevant information."""
        results = []
        
        for family_id, archive in self.family_archives.items():
            # Simple keyword matching in knowledge index
            query_words = set(query.lower().split())
            
            for topic, relevant_agents in archive.knowledge_index.items():
                topic_words = set(topic.lower().split())
                
                # Check for word overlap
                if query_words & topic_words:
                    # Found relevant topic, access archived agents
                    for agent_id in relevant_agents:
                        # Simulate archive access
                        archive_data = await self._access_archived_agent(agent_id, query)
                        if archive_data:
                            results.append(archive_data)
                            
                            # Update access patterns
                            archive.access_patterns[agent_id] = archive.access_patterns.get(agent_id, 0) + 1
        
        if results:
            # Combine and synthesize results
            return self._synthesize_archive_results(results, query)
        
        return None
    
    async def _access_archived_agent(self, agent_id: str, query: str) -> Optional[Dict[str, Any]]:
        """Access archived agent for specific information."""
        # Simulate archived agent access
        # In a real implementation, this would access stored agent knowledge
        
        return {
            "agent_id": agent_id,
            "response": f"Archived response from {agent_id} for query: {query}",
            "confidence": 0.7,
            "knowledge_type": "archived_learning"
        }
    
    def _synthesize_archive_results(self, results: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """Synthesize multiple archive results into a coherent response."""
        if not results:
            return None
        
        # Simple synthesis - combine responses and calculate average confidence
        combined_response = []
        total_confidence = 0
        
        for result in results:
            combined_response.append(result.get("response", ""))
            total_confidence += result.get("confidence", 0)
        
        return {
            "synthesized_response": " | ".join(combined_response),
            "source_agents": [r.get("agent_id") for r in results],
            "average_confidence": total_confidence / len(results),
            "synthesis_method": "simple_concatenation"
        }
    
    async def _coordinate_with_siblings(self, query: str, request: InformationRequest) -> Optional[Any]:
        """Coordinate with sibling apprentice agents for information."""
        if not self.sibling_apprentices:
            return None
        
        # Send request to sibling apprentices
        responses = []
        
        for sibling_id in self.sibling_apprentices:
            # Simulate coordination message
            coordination_message = {
                "type": "information_coordination",
                "query": query,
                "request_id": request.request_id,
                "priority": request.priority
            }
            
            # In a real implementation, this would send actual messages
            sibling_response = await self._simulate_sibling_response(sibling_id, coordination_message)
            if sibling_response:
                responses.append(sibling_response)
        
        if responses:
            # Select best response or combine them
            return self._select_best_sibling_response(responses)
        
        return None
    
    async def _simulate_sibling_response(self, sibling_id: str, coordination_message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Simulate response from sibling apprentice agent."""
        # In a real implementation, this would be actual inter-agent communication
        
        # Simulate that 30% of siblings have relevant information
        import random
        if random.random() < 0.3:
            return {
                "sibling_id": sibling_id,
                "response": f"Information from {sibling_id}: {coordination_message['query']}",
                "confidence": random.uniform(0.6, 0.9),
                "response_time": random.uniform(0.1, 0.5)
            }
        
        return None
    
    def _select_best_sibling_response(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select the best response from sibling coordination."""
        if not responses:
            return None
        
        # Select response with highest confidence
        best_response = max(responses, key=lambda r: r.get("confidence", 0))
        
        return {
            "best_response": best_response["response"],
            "source_sibling": best_response["sibling_id"],
            "confidence": best_response["confidence"],
            "coordination_success": True,
            "alternative_responses": len(responses) - 1
        }
    
    def _generate_guidance(self, query: str, request: InformationRequest) -> Dict[str, Any]:
        """Generate guidance when direct information is not available."""
        guidance = {
            "message": f"No direct information found for: {query}",
            "suggestions": [],
            "alternative_approaches": [],
            "family_recommendations": []
        }
        
        # Generate suggestions based on query type
        query_lower = query.lower()
        
        if "how" in query_lower:
            guidance["suggestions"].append("Try breaking down the 'how' question into specific steps")
            guidance["alternative_approaches"].append("Look for related process documentation")
        
        if "what" in query_lower:
            guidance["suggestions"].append("Try searching for definitions or examples")
            guidance["alternative_approaches"].append("Look for categorical information")
        
        if "why" in query_lower:
            guidance["suggestions"].append("Look for causal relationships or explanations")
            guidance["alternative_approaches"].append("Search for reasoning or justification")
        
        # Family-specific recommendations
        if self.family_archives:
            guidance["family_recommendations"].append("Check with parent learning agents for deeper analysis")
            guidance["family_recommendations"].append("Consider consulting archived family knowledge")
        
        if self.sibling_apprentices:
            guidance["family_recommendations"].append("Coordinate with sibling apprentices for distributed search")
        
        return guidance
    
    def _add_to_cache(self, query: str, result: Any, source: str) -> None:
        """Add result to information cache."""
        query_hash = self._hash_query(query)
        
        # Check cache size limit
        if len(self.information_cache) >= self.communication_protocols["max_cache_size"]:
            self._evict_cache_entries()
        
        # Create cache entry
        entry = CacheEntry(
            cache_id=f"cache_{query_hash}_{int(time.time())}",
            query=query,
            result=result,
            source_agent=source,
            expiry_time=time.time() + self.communication_protocols["cache_ttl"]
        )
        
        self.information_cache[query_hash] = entry
        
        LOG.debug(f"AA {self.agent_id} cached result for query: {query[:30]}...")
    
    def _evict_cache_entries(self) -> None:
        """Evict least recently used cache entries."""
        # Sort by last accessed time and remove oldest entries
        sorted_entries = sorted(
            self.information_cache.items(),
            key=lambda x: x[1].last_accessed
        )
        
        # Remove oldest 20% of entries
        remove_count = len(sorted_entries) // 5
        for i in range(remove_count):
            query_hash, entry = sorted_entries[i]
            del self.information_cache[query_hash]
        
        LOG.debug(f"AA {self.agent_id} evicted {remove_count} cache entries")
    
    async def _handle_family_coordination(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle family coordination tasks."""
        coordination_type = input_data.get("coordination_type", "general")
        
        if coordination_type == "add_sibling":
            sibling_id = input_data.get("sibling_id")
            if sibling_id:
                self.sibling_apprentices.add(sibling_id)
                LOG.info(f"AA {self.agent_id} added sibling: {sibling_id}")
                return {"success": True, "action": "sibling_added", "sibling_id": sibling_id}
        
        elif coordination_type == "sync_cache":
            # Coordinate cache synchronization with siblings
            sync_results = await self._synchronize_caches()
            return {"success": True, "action": "cache_sync", "results": sync_results}
        
        elif coordination_type == "archive_update":
            # Update family archive information
            archive_data = input_data.get("archive_data", {})
            update_results = self._update_family_archive(archive_data)
            return {"success": True, "action": "archive_update", "results": update_results}
        
        return {"success": False, "error": "Unknown coordination type"}
    
    async def _synchronize_caches(self) -> Dict[str, Any]:
        """Synchronize caches with sibling apprentices."""
        sync_stats = {
            "entries_shared": 0,
            "entries_received": 0,
            "conflicts_resolved": 0
        }
        
        # Share popular cache entries with siblings
        popular_entries = sorted(
            self.information_cache.values(),
            key=lambda e: e.access_count,
            reverse=True
        )[:10]  # Share top 10 most accessed entries
        
        for entry in popular_entries:
            # Simulate sharing with siblings
            sync_stats["entries_shared"] += 1
        
        # Simulate receiving entries from siblings
        # In real implementation, this would involve actual communication
        sync_stats["entries_received"] = len(self.sibling_apprentices) * 3  # Assume 3 entries per sibling
        
        LOG.info(f"AA {self.agent_id} synchronized cache with {len(self.sibling_apprentices)} siblings")
        
        return sync_stats
    
    def _update_family_archive(self, archive_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update family archive with new information."""
        family_id = archive_data.get("family_id", self.family_id)
        
        if family_id not in self.family_archives:
            self.family_archives[family_id] = FamilyArchive(
                family_id=family_id,
                archived_members=[],
                knowledge_index={},
                access_patterns={}
            )
        
        archive = self.family_archives[family_id]
        
        # Add new archived members
        new_members = archive_data.get("new_members", [])
        for member_id in new_members:
            if member_id not in archive.archived_members:
                archive.archived_members.append(member_id)
                archive.access_patterns[member_id] = 0
        
        # Update knowledge index
        new_knowledge = archive_data.get("knowledge_index", {})
        for topic, agents in new_knowledge.items():
            if topic in archive.knowledge_index:
                # Merge agent lists
                existing_agents = set(archive.knowledge_index[topic])
                new_agents = set(agents)
                archive.knowledge_index[topic] = list(existing_agents | new_agents)
            else:
                archive.knowledge_index[topic] = agents
        
        return {
            "family_id": family_id,
            "members_added": len(new_members),
            "topics_updated": len(new_knowledge),
            "total_archived_members": len(archive.archived_members)
        }
    
    async def _handle_cache_management(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle cache management operations."""
        operation = input_data.get("operation", "status")
        
        if operation == "status":
            return self._get_cache_status()
        elif operation == "clear":
            self.information_cache.clear()
            return {"success": True, "action": "cache_cleared"}
        elif operation == "optimize":
            optimization_results = self._optimize_cache()
            return {"success": True, "action": "cache_optimized", "results": optimization_results}
        
        return {"success": False, "error": "Unknown cache operation"}
    
    def _get_cache_status(self) -> Dict[str, Any]:
        """Get current cache status."""
        if not self.information_cache:
            return {
                "cache_size": 0,
                "cache_utilization": 0.0,
                "hit_rate": 0.0,
                "expired_entries": 0
            }
        
        current_time = time.time()
        expired_count = 0
        total_access_count = 0
        
        for entry in self.information_cache.values():
            if entry.expiry_time and current_time > entry.expiry_time:
                expired_count += 1
            total_access_count += entry.access_count
        
        return {
            "cache_size": len(self.information_cache),
            "cache_utilization": len(self.information_cache) / self.communication_protocols["max_cache_size"],
            "average_access_count": total_access_count / len(self.information_cache),
            "expired_entries": expired_count,
            "cache_efficiency": (total_access_count - expired_count) / max(total_access_count, 1)
        }
    
    def _optimize_cache(self) -> Dict[str, Any]:
        """Optimize cache by removing expired and low-value entries."""
        current_time = time.time()
        removed_expired = 0
        removed_low_value = 0
        
        # Remove expired entries
        expired_hashes = []
        for query_hash, entry in self.information_cache.items():
            if entry.expiry_time and current_time > entry.expiry_time:
                expired_hashes.append(query_hash)
        
        for query_hash in expired_hashes:
            del self.information_cache[query_hash]
            removed_expired += 1
        
        # Remove low-value entries (low access count and old)
        low_value_threshold = 2
        old_threshold = current_time - 3600  # 1 hour old
        
        low_value_hashes = []
        for query_hash, entry in self.information_cache.items():
            if entry.access_count < low_value_threshold and entry.last_accessed < old_threshold:
                low_value_hashes.append(query_hash)
        
        for query_hash in low_value_hashes:
            del self.information_cache[query_hash]
            removed_low_value += 1
        
        return {
            "expired_removed": removed_expired,
            "low_value_removed": removed_low_value,
            "remaining_entries": len(self.information_cache)
        }
    
    async def _handle_archive_access(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle direct archive access requests."""
        archive_operation = input_data.get("operation", "search")
        
        if archive_operation == "search":
            query = input_data.get("query", "")
            family_id = input_data.get("family_id")
            
            if family_id and family_id in self.family_archives:
                result = await self._search_specific_archive(family_id, query)
                return {"success": True, "operation": "archive_search", "result": result}
            else:
                # Search all archives
                all_results = []
                for fid in self.family_archives:
                    result = await self._search_specific_archive(fid, query)
                    if result:
                        all_results.append({"family_id": fid, "result": result})
                
                return {"success": True, "operation": "multi_archive_search", "results": all_results}
        
        elif archive_operation == "list":
            archive_list = []
            for family_id, archive in self.family_archives.items():
                archive_list.append({
                    "family_id": family_id,
                    "member_count": len(archive.archived_members),
                    "topic_count": len(archive.knowledge_index),
                    "creation_time": archive.creation_time
                })
            
            return {"success": True, "operation": "archive_list", "archives": archive_list}
        
        return {"success": False, "error": "Unknown archive operation"}
    
    async def _search_specific_archive(self, family_id: str, query: str) -> Optional[Dict[str, Any]]:
        """Search a specific family archive."""
        if family_id not in self.family_archives:
            return None
        
        archive = self.family_archives[family_id]
        results = []
        
        # Search through knowledge index
        query_words = set(query.lower().split())
        
        for topic, agents in archive.knowledge_index.items():
            topic_words = set(topic.lower().split())
            overlap = len(query_words & topic_words)
            
            if overlap > 0:
                # Found relevant topic
                relevance_score = overlap / len(query_words | topic_words)
                
                for agent_id in agents:
                    agent_result = await self._access_archived_agent(agent_id, query)
                    if agent_result:
                        agent_result["relevance_score"] = relevance_score
                        agent_result["topic"] = topic
                        results.append(agent_result)
        
        if results:
            # Sort by relevance and return top results
            results.sort(key=lambda r: r.get("relevance_score", 0), reverse=True)
            return {
                "family_id": family_id,
                "query": query,
                "results": results[:5],  # Top 5 results
                "total_matches": len(results)
            }
        
        return None
    
    async def _handle_general_request(self, input_data: Any) -> Dict[str, Any]:
        """Handle general requests that don't fit other categories."""
        return {
            "message": "General request processed",
            "input_received": str(input_data)[:100],
            "processed_by": self.agent_id,
            "agent_type": self.agent_type.value,
            "success": True,
            "guidance": "For better assistance, please specify request type (information_request, family_coordination, etc.)"
        }
    
    def _update_access_statistics(self, request_type: str, requester_id: str) -> None:
        """Update access statistics for monitoring."""
        current_time = time.time()
        
        if request_type not in self.access_statistics:
            self.access_statistics[request_type] = {
                "count": 0,
                "last_access": current_time,
                "requesters": {}
            }
        
        stats = self.access_statistics[request_type]
        stats["count"] += 1
        stats["last_access"] = current_time
        
        if requester_id not in stats["requesters"]:
            stats["requesters"][requester_id] = 0
        stats["requesters"][requester_id] += 1
    
    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle messages from other agents."""
        if message.content.get("type") == "information_coordination":
            # Handle coordination request from sibling
            query = message.content.get("query", "")
            request_id = message.content.get("request_id", "")
            
            # Search local resources
            result = await self._search_family_archives(query)
            
            if result:
                return self.send_message(
                    message.sender_id,
                    message.sender_type,
                    {
                        "type": "coordination_response",
                        "request_id": request_id,
                        "result": result,
                        "confidence": 0.8
                    }
                )
            else:
                return self.send_message(
                    message.sender_id,
                    message.sender_type,
                    {
                        "type": "coordination_response",
                        "request_id": request_id,
                        "result": None,
                        "message": "No relevant information found"
                    }
                )
        
        elif message.content.get("type") == "cache_sync_request":
            # Handle cache synchronization request
            shared_entries = message.content.get("cache_entries", [])
            
            # Process shared cache entries
            for entry_data in shared_entries:
                if self._should_accept_cache_entry(entry_data):
                    self._integrate_external_cache_entry(entry_data)
            
            return self.send_message(
                message.sender_id,
                message.sender_type,
                {
                    "type": "cache_sync_response",
                    "entries_accepted": len(shared_entries),
                    "status": "completed"
                }
            )
        
        elif message.content.get("type") == "archive_notification":
            # Handle notification of new archived agent
            archive_data = message.content.get("archive_data", {})
            update_result = self._update_family_archive(archive_data)
            
            LOG.info(f"AA {self.agent_id} received archive notification")
            
            return None  # No response needed for notifications
        
        return None
    
    def _should_accept_cache_entry(self, entry_data: Dict[str, Any]) -> bool:
        """Determine if an external cache entry should be accepted."""
        # Simple acceptance criteria
        query = entry_data.get("query", "")
        access_count = entry_data.get("access_count", 0)
        
        # Accept if query is not already cached and has reasonable access count
        query_hash = self._hash_query(query)
        return query_hash not in self.information_cache and access_count > 1
    
    def _integrate_external_cache_entry(self, entry_data: Dict[str, Any]) -> None:
        """Integrate an external cache entry into local cache."""
        query = entry_data.get("query", "")
        result = entry_data.get("result")
        source = entry_data.get("source", "external")
        
        if query and result:
            self._add_to_cache(query, result, f"external_{source}")
    
    def add_sibling_apprentice(self, sibling_id: str) -> None:
        """Add a sibling apprentice for coordination."""
        self.sibling_apprentices.add(sibling_id)
        LOG.info(f"AA {self.agent_id} added sibling apprentice: {sibling_id}")
    
    def get_apprentice_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about apprentice performance."""
        cache_stats = self._get_cache_status()
        
        return {
            "agent_id": self.agent_id,
            "family_id": self.family_id,
            "parent_id": self.parent_id,
            "sibling_count": len(self.sibling_apprentices),
            "family_archives_count": len(self.family_archives),
            "cache_statistics": cache_stats,
            "access_statistics": self.access_statistics.copy(),
            "total_requests_processed": sum(stats["count"] for stats in self.access_statistics.values()),
            "most_active_requester": max(
                (
                    requester_id 
                    for stats in self.access_statistics.values() 
                    for requester_id in stats["requesters"]
                ),
                key=lambda rid: sum(
                    stats["requesters"].get(rid, 0) 
                    for stats in self.access_statistics.values()
                ),
                default="none"
            ) if self.access_statistics else "none"
        }