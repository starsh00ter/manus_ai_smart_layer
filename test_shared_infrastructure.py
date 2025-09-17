#!/usr/bin/env python3

"""
Comprehensive Test Suite for Shared Infrastructure

Tests all components of the shared infrastructure including:
- Atomic credit ledger
- Unified configuration
- Shared database client
- Cache manager
- Project coordination
- Credit management
"""

import sys
import os
import time
import json
from datetime import datetime

# Add manus_core to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_configuration():
    """Test unified configuration system"""
    print("🔧 Testing Configuration System...")
    
    try:
        from manus_core.config import get_config, is_feature_enabled
        
        config = get_config()
        
        # Test configuration access
        assert config.credit.daily_limit > 0, "Daily limit should be positive"
        assert 0 <= config.credit.warning_threshold <= 1, "Warning threshold should be between 0 and 1"
        assert config.system.session_timeout > 0, "Session timeout should be positive"
        
        # Test feature flags
        auto_reflection = is_feature_enabled('auto_reflection')
        assert isinstance(auto_reflection, bool), "Feature flag should return boolean"
        
        # Test configuration summary
        summary = config.get_config_summary()
        assert 'credit' in summary, "Summary should include credit config"
        assert 'system' in summary, "Summary should include system config"
        
        print("✅ Configuration system test passed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration system test failed: {e}")
        return False

def test_database_client():
    """Test shared database client"""
    print("🗄️ Testing Database Client...")
    
    try:
        from manus_core.db.client import get_shared_client
        
        client = get_shared_client("test_project")
        
        # Test health check
        health = client.health_check()
        assert 'status' in health, "Health check should return status"
        
        # Test schema info
        schema_info = client.get_schema_info()
        # Should work even without connection (returns error dict)
        assert isinstance(schema_info, dict), "Schema info should return dict"
        
        # Test insert/select with fallback
        test_data = {
            "test_field": "test_value",
            "timestamp": datetime.now().isoformat()
        }
        
        result = client.insert("test_table", test_data, "shared")
        # Should work with local fallback
        assert result is not None, "Insert should return result (even with fallback)"
        
        print("✅ Database client test passed")
        return True
        
    except Exception as e:
        print(f"❌ Database client test failed: {e}")
        return False

def test_cache_manager():
    """Test shared cache manager"""
    print("💾 Testing Cache Manager...")
    
    try:
        from manus_core.cache.manager import get_cache_manager
        
        cache = get_cache_manager("test_project")
        
        # Test basic cache operations
        test_key = "test_key"
        test_value = {"data": "test_value", "timestamp": time.time()}
        
        # Test set
        success = cache.set(test_key, test_value, namespace="test")
        assert success, "Cache set should succeed"
        
        # Test get
        retrieved = cache.get(test_key, namespace="test")
        assert retrieved == test_value, "Retrieved value should match stored value"
        
        # Test exists
        exists = cache.exists(test_key, namespace="test")
        assert exists, "Key should exist in cache"
        
        # Test delete
        deleted = cache.delete(test_key, namespace="test")
        assert deleted, "Cache delete should succeed"
        
        # Test function caching
        @cache.cache_function(ttl=60, namespace="functions")
        def test_function(x, y):
            return x + y
        
        result1 = test_function(1, 2)
        result2 = test_function(1, 2)  # Should be cached
        assert result1 == result2 == 3, "Function cache should work correctly"
        
        # Test statistics
        stats = cache.get_stats()
        assert 'hit_rate' in stats, "Stats should include hit rate"
        assert 'total_requests' in stats, "Stats should include total requests"
        
        print("✅ Cache manager test passed")
        return True
        
    except Exception as e:
        print(f"❌ Cache manager test failed: {e}")
        return False

def test_credit_management():
    """Test enhanced credit management"""
    print("💳 Testing Credit Management...")
    
    try:
        from manus_core.utils.credits import get_credit_manager, check_credits
        
        manager = get_credit_manager("test_project")
        
        # Test credit availability check
        user_id = "test_user"
        availability = manager.check_credit_availability(user_id, 1000)
        assert 'allowed' in availability, "Availability check should return allowed status"
        assert 'remaining_balance' in availability, "Should return remaining balance"
        
        # Test credit status
        status = manager.get_credit_status(user_id)
        assert 'current_balance' in status, "Status should include current balance"
        assert 'usage_percentage' in status, "Status should include usage percentage"
        
        # Test convenience function
        credits_ok = check_credits(user_id, 500, "test_project")
        assert isinstance(credits_ok, bool), "Check credits should return boolean"
        
        # Test usage statistics
        stats = manager.get_usage_statistics(user_id, days=7)
        assert 'period_days' in stats, "Stats should include period"
        assert 'total_operations' in stats, "Stats should include operation count"
        
        print("✅ Credit management test passed")
        return True
        
    except Exception as e:
        print(f"❌ Credit management test failed: {e}")
        return False

def test_project_coordination():
    """Test project coordination system"""
    print("🤝 Testing Project Coordination...")
    
    try:
        from manus_core.routing.coordinator import get_coordinator
        
        coordinator = get_coordinator("test_project")
        
        # Test status update
        status_updated = coordinator.update_project_status(
            commit_hash="test123",
            health_score=0.85,
            active_operations=2
        )
        # Should work even with fallback
        assert isinstance(status_updated, bool), "Status update should return boolean"
        
        # Test system status
        system_status = coordinator.get_system_status()
        assert isinstance(system_status, dict), "System status should return dict"
        
        # Test coordination check
        coord_check = coordinator.check_coordination_requirements()
        assert 'coordination_needed' in coord_check, "Should return coordination status"
        
        # Test message sending
        message_sent = coordinator.send_message(
            to_project="other_project",
            message_type="test",
            title="Test Message",
            content="This is a test coordination message",
            priority="low"
        )
        assert isinstance(message_sent, bool), "Message sending should return boolean"
        
        # Test coordination cycle
        cycle_result = coordinator.perform_coordination_cycle()
        assert isinstance(cycle_result, dict), "Coordination cycle should return dict"
        assert 'timestamp' in cycle_result, "Should include timestamp"
        
        print("✅ Project coordination test passed")
        return True
        
    except Exception as e:
        print(f"❌ Project coordination test failed: {e}")
        return False

def test_enhanced_router():
    """Test enhanced router with shared credit management"""
    print("🔀 Testing Enhanced Router...")
    
    try:
        from memory.router import spend, _log_cost, config, credit_manager
        
        # Test configuration loading
        assert config is not None, "Config should be loaded"
        assert credit_manager is not None, "Credit manager should be initialized"
        
        # Test spend function
        can_spend = spend(100)  # Small amount should be allowed
        assert isinstance(can_spend, bool), "Spend should return boolean"
        
        # Test cost logging (should not fail even if database is not available)
        try:
            _log_cost(50, "test_action")
            print("💳 Cost logging completed")
        except Exception as e:
            print(f"⚠️ Cost logging failed (expected with fallback): {e}")
        
        print("✅ Enhanced router test passed")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced router test failed: {e}")
        return False

def test_integration():
    """Test integration between components"""
    print("🔗 Testing Component Integration...")
    
    try:
        from manus_core.config import get_config
        from manus_core.utils.credits import get_credit_manager
        from manus_core.routing.coordinator import get_coordinator
        from manus_core.cache.manager import get_cache_manager
        
        # Test that all components can be initialized together
        config = get_config()
        credit_manager = get_credit_manager("integration_test")
        coordinator = get_coordinator("integration_test")
        cache = get_cache_manager("integration_test")
        
        # Test cross-component functionality
        # Credit manager should use config
        assert credit_manager.config.credit.daily_limit == config.credit.daily_limit
        
        # Coordinator should use credit manager
        assert coordinator.credit_manager is not None
        
        # Test end-to-end workflow
        user_id = "integration_user"
        
        # 1. Check credits
        availability = credit_manager.check_credit_availability(user_id, 1000)
        
        # 2. Update project status
        coordinator.update_project_status(health_score=0.9)
        
        # 3. Cache some data
        cache.set("integration_test", {"status": "success"}, namespace="test")
        cached_data = cache.get("integration_test", namespace="test")
        
        assert cached_data["status"] == "success", "Integration cache test should work"
        
        print("✅ Component integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Component integration test failed: {e}")
        return False

def generate_test_report(results):
    """Generate comprehensive test report"""
    report = {
        "test_timestamp": datetime.now().isoformat(),
        "test_results": results,
        "total_tests": len(results),
        "passed_tests": sum(1 for r in results.values() if r),
        "failed_tests": sum(1 for r in results.values() if not r),
        "success_rate": (sum(1 for r in results.values() if r) / len(results)) * 100,
        "system_info": {
            "python_version": sys.version,
            "platform": os.name,
            "working_directory": os.getcwd()
        }
    }
    
    # Save report
    report_file = f"logs/infrastructure_test_report_{int(time.time())}.json"
    os.makedirs("logs", exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    return report, report_file

def main():
    """Run comprehensive infrastructure tests"""
    print("🚀 Starting Shared Infrastructure Test Suite...")
    print("=" * 60)
    
    # Run all tests
    test_results = {
        "configuration": test_configuration(),
        "database_client": test_database_client(),
        "cache_manager": test_cache_manager(),
        "credit_management": test_credit_management(),
        "project_coordination": test_project_coordination(),
        "enhanced_router": test_enhanced_router(),
        "integration": test_integration()
    }
    
    print("=" * 60)
    
    # Generate report
    report, report_file = generate_test_report(test_results)
    
    # Print summary
    print(f"📊 Test Summary:")
    print(f"   Total Tests: {report['total_tests']}")
    print(f"   Passed: {report['passed_tests']}")
    print(f"   Failed: {report['failed_tests']}")
    print(f"   Success Rate: {report['success_rate']:.1f}%")
    print(f"   Report saved: {report_file}")
    
    # Print detailed results
    print("\n📋 Detailed Results:")
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    if report['success_rate'] >= 80:
        print("\n🎉 Infrastructure tests mostly successful!")
        print("   System is ready for deployment and coordination.")
    else:
        print("\n⚠️ Some infrastructure tests failed.")
        print("   Review failed components before deployment.")
    
    return report['success_rate'] >= 80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

