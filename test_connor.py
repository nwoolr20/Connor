"""
Test script for the Connor Agent System

This script demonstrates and tests the Connor multi-agent system functionality.
"""

import asyncio
import sys
import os

# Add the forge directory to the Python path
sys.path.append('/home/runner/work/Connor/Connor/autogpts/forge')

from forge.connor import ConnorSystem
from forge.connor.base import AgentConfig, AgentType, AgentPhase

async def test_connor_system():
    """Test the Connor multi-agent system."""
    print("🚀 Testing Connor Multi-Agent System")
    print("=" * 50)
    
    # Initialize Connor system
    print("\n1. Initializing Connor System...")
    connor = ConnorSystem()
    
    # Check system status
    status = connor.get_system_status()
    print(f"   ✅ System initialized with {status['total_agents']} agents")
    print(f"   📊 Agent distribution: {status['agent_distribution']}")
    print(f"   👨‍👩‍👧‍👦 Families: {status['families']}")
    
    # Test simple input processing
    print("\n2. Testing Simple Question Processing...")
    test_inputs = [
        "What is the capital of France?",
        "How do I create a Python function?",
        "Please write a simple hello world program",
        "Can you explain machine learning?"
    ]
    
    for i, test_input in enumerate(test_inputs, 1):
        print(f"\n   Test {i}: {test_input}")
        try:
            response = await connor.process_input(test_input, priority=2)
            
            print(f"   ✅ Success: {response['success']}")
            print(f"   🤖 Final Answer: {response['final_answer'][:100]}...")
            print(f"   📊 Confidence: {response['system_confidence']:.1%}")
            print(f"   ⏱️  Processing Time: {response['processing_time']:.2f}s")
            
            # Show agent involvement
            stages = response.get('processing_stages', {})
            agents_involved = []
            for stage_name, stage_data in stages.items():
                if stage_data:
                    agents_involved.append(stage_name.upper())
            print(f"   🔄 Agents Involved: {' → '.join(agents_involved)}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test family expansion
    print("\n3. Testing Learning Agent Family Expansion...")
    try:
        original_families = len(connor.family_registry)
        
        # Expand existing family
        family_id = list(connor.family_registry.keys())[0]
        new_children = await connor.expand_family(family_id, num_children=2)
        
        print(f"   ✅ Expanded family {family_id} with {len(new_children)} children")
        
        # Create new family
        new_family_id = await connor.create_learning_agent_family()
        print(f"   ✅ Created new family: {new_family_id}")
        
        # Check updated status
        updated_status = connor.get_system_status()
        print(f"   📊 Total families now: {updated_status['families']} (was {original_families})")
        print(f"   🤖 Total agents now: {updated_status['total_agents']}")
        
    except Exception as e:
        print(f"   ❌ Error in family expansion: {e}")
    
    # Test complex processing
    print("\n4. Testing Complex Multi-Step Processing...")
    complex_input = "I need to create a comprehensive business plan for a tech startup that focuses on AI-powered educational tools. Please help me outline the key components, market analysis, and implementation strategy."
    
    try:
        response = await connor.process_input(complex_input, priority=1)  # High priority
        
        print(f"   ✅ Complex request processed successfully")
        print(f"   🎯 Goal Created: {response['processing_stages']['gap']['goal_created'][:80]}...")
        print(f"   📋 Plan Steps: {response['processing_stages']['gap']['plan_steps']}")
        print(f"   🧠 Learning Agents Consulted: {response['processing_stages']['la_monitoring']['agents_consulted']}")
        print(f"   ⚖️  Alternatives Evaluated: {response['processing_stages']['uba_optimization']['alternatives_considered']}")
        print(f"   📊 System Confidence: {response['system_confidence']:.1%}")
        
    except Exception as e:
        print(f"   ❌ Error in complex processing: {e}")
    
    # Test system performance metrics
    print("\n5. System Performance Metrics...")
    final_status = connor.get_system_status()
    metrics = final_status['system_metrics']
    
    print(f"   📈 Total Requests Processed: {metrics['total_processed']}")
    print(f"   ✅ Success Rate: {metrics['success_rate']:.1%}")
    print(f"   ⏱️  Average Processing Time: {metrics['avg_processing_time']:.2f}s")
    
    # Show family details
    print(f"\n   👨‍👩‍👧‍👦 Family Details:")
    for family_id, family_info in final_status['family_details'].items():
        print(f"      {family_id}: {family_info['children_count']} children, {family_info['apprentices_count']} apprentices")
    
    # Shutdown system
    print("\n6. Shutting down Connor System...")
    await connor.shutdown()
    print("   ✅ System shutdown complete")
    
    print("\n" + "=" * 50)
    print("🎉 Connor System Test Completed Successfully!")
    print("=" * 50)

async def test_individual_agents():
    """Test individual agent types."""
    print("\n🔬 Testing Individual Agent Types")
    print("=" * 50)
    
    # Test SRA
    print("\n1. Testing Simple Reflex Agent (SRA)...")
    from forge.connor.sra import SimpleReflexAgent
    
    sra_config = AgentConfig(
        agent_id="test_sra",
        agent_type=AgentType.SRA
    )
    sra = SimpleReflexAgent(sra_config)
    
    sra_result = await sra.process_input("What is machine learning?")
    print(f"   ✅ SRA Classification: {sra_result['input_type']}")
    print(f"   🏷️  Tags: {sra_result['tags']}")
    print(f"   📤 Routing: {sra_result['routing']['next_agent']}")
    
    # Test MBR
    print("\n2. Testing Model-Based Reflex Agent (MBR)...")
    from forge.connor.mbr import ModelBasedReflexAgent
    
    mbr_config = AgentConfig(
        agent_id="test_mbr",
        agent_type=AgentType.MBR
    )
    mbr = ModelBasedReflexAgent(mbr_config)
    
    mbr_result = await mbr.process_input(sra_result)
    print(f"   ✅ MBR Analysis: {mbr_result['analysis']['complexity']}")
    print(f"   🎯 Intent: {mbr_result['analysis']['intent']}")
    print(f"   📊 Confidence: {mbr_result['confidence']:.1%}")
    
    # Test GAP
    print("\n3. Testing Goal-Based Agent-Planner (GAP)...")
    from forge.connor.gap import GoalBasedAgentPlanner
    
    gap_config = AgentConfig(
        agent_id="test_gap",
        agent_type=AgentType.GAP
    )
    gap = GoalBasedAgentPlanner(gap_config)
    
    gap_result = await gap.process_input(mbr_result)
    print(f"   ✅ Goal: {gap_result['goal']['description'][:60]}...")
    print(f"   📋 Plan Actions: {len(gap_result['plan']['actions'])}")
    print(f"   ⏱️  Estimated Time: {gap_result['estimated_completion']:.1f} minutes")
    
    # Test LA
    print("\n4. Testing Learning Agent (LA)...")
    from forge.connor.la import LearningAgent
    
    la_config = AgentConfig(
        agent_id="test_la",
        agent_type=AgentType.LA,
        phase=AgentPhase.CHILD
    )
    la = LearningAgent(la_config)
    
    la_result = await la.process_input(gap_result)
    print(f"   ✅ Phase: {la_result['phase']}")
    print(f"   🧠 Patterns Applied: {len(la_result['matching_patterns'])}")
    print(f"   📊 Learning Confidence: {la_result['confidence']:.1%}")
    
    # Test UBA
    print("\n5. Testing Utility-Based Agent (UBA)...")
    from forge.connor.uba import UtilityBasedAgent
    
    uba_config = AgentConfig(
        agent_id="test_uba",
        agent_type=AgentType.UBA
    )
    uba = UtilityBasedAgent(uba_config)
    
    uba_result = await uba.process_input(la_result)
    print(f"   ✅ Alternatives: {uba_result['alternatives_considered']}")
    print(f"   🎯 Selected: {uba_result['selected_alternative']}")
    print(f"   📊 Expected Utility: {uba_result['expected_utility']:.3f}")
    
    # Test AA
    print("\n6. Testing Apprentice Agent (AA)...")
    from forge.connor.aa import ApprenticeAgent
    
    aa_config = AgentConfig(
        agent_id="test_aa",
        agent_type=AgentType.AA,
        family_id="test_family"
    )
    aa = ApprenticeAgent(aa_config)
    
    aa_result = await aa.process_input({
        "type": "information_request",
        "query": "How does machine learning work?",
        "requester_id": "test_user"
    })
    print(f"   ✅ Request Processed: {aa_result['success']}")
    print(f"   💾 Cache Hit: {aa_result.get('cache_hit', False)}")
    print(f"   📚 Source: {aa_result.get('source', 'N/A')}")
    
    print("\n" + "=" * 50)
    print("🎉 Individual Agent Tests Completed!")
    print("=" * 50)

if __name__ == "__main__":
    async def main():
        """Run all tests."""
        try:
            await test_individual_agents()
            await test_connor_system()
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
    
    # Run the tests
    asyncio.run(main())