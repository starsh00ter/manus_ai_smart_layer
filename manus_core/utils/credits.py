#!/usr/bin/env python3

"""
Enhanced Credit Management System

Provides atomic credit operations, transaction safety, and comprehensive
credit tracking for both Manus AI projects.
"""

import time
import uuid
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from contextlib import contextmanager
from datetime import datetime, timedelta

from ..config import get_config
from ..db.client import get_shared_client

class CreditGuardError(Exception):
    """Exception raised for credit-related errors"""
    pass

@dataclass
class CreditTransaction:
    """Represents a credit transaction"""
    transaction_id: str
    user_id: str
    operation_id: str
    operation_type: str
    tokens_estimated: int
    tokens_actual: int
    cost_estimate: float
    cost_actual: float
    transaction_type: str  # 'DEBIT', 'CREDIT'
    status: str  # 'PENDING', 'COMPLETED', 'FAILED', 'REFUNDED'
    created_at: datetime
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None

class CreditManager:
    """Enhanced credit manager with atomic operations"""
    
    def __init__(self, project_name: str = "smart_layer"):
        self.project_name = project_name
        self.config = get_config()
        self.db_client = get_shared_client(project_name)
        self._lock = threading.RLock()
        self._pending_transactions = {}
        
    @contextmanager
    def atomic_transaction(self, user_id: str, operation_id: str):
        """Provide atomic credit transaction context"""
        transaction_id = str(uuid.uuid4())
        
        try:
            with self._lock:
                yield transaction_id
        except Exception as e:
            # Rollback any pending transactions
            self._rollback_transaction(transaction_id, str(e))
            raise
    
    def check_credit_availability(self, user_id: str, estimated_tokens: int) -> Dict[str, Any]:
        """Check if credits are available for an operation"""
        try:
            # Use database function for atomic check
            if self.db_client.client:
                result = self.db_client.rpc('check_credit_availability', {
                    'p_user_id': user_id,
                    'p_estimated_tokens': estimated_tokens
                })
                
                if result:
                    return result[0] if isinstance(result, list) else result
            
            # Fallback to local calculation
            return self._local_credit_check(user_id, estimated_tokens)
            
        except Exception as e:
            print(f"❌ Credit availability check failed: {e}")
            return {
                "allowed": False,
                "error": str(e),
                "remaining_balance": 0,
                "usage_percentage": 100.0
            }
    
    def _local_credit_check(self, user_id: str, estimated_tokens: int) -> Dict[str, Any]:
        """Local fallback for credit checking"""
        # Get recent credit usage from local cache or database
        recent_usage = self._get_recent_usage(user_id)
        daily_limit = self.config.credit.daily_limit
        
        used_today = sum(usage.get('tokens_actual', 0) for usage in recent_usage)
        remaining = daily_limit - used_today
        
        if remaining >= estimated_tokens:
            return {
                "allowed": True,
                "remaining_balance": remaining,
                "estimated_tokens": estimated_tokens,
                "usage_percentage": (used_today / daily_limit) * 100
            }
        else:
            return {
                "allowed": False,
                "remaining_balance": remaining,
                "estimated_tokens": estimated_tokens,
                "shortage": estimated_tokens - remaining,
                "usage_percentage": (used_today / daily_limit) * 100
            }
    
    def _get_recent_usage(self, user_id: str) -> List[Dict[str, Any]]:
        """Get recent credit usage for user"""
        try:
            # Get today's usage from database
            today = datetime.now().date()
            
            usage_data = self.db_client.select(
                table="credit_ledger",
                columns="tokens_actual, cost_actual, operation_type",
                filters={
                    "user_id": user_id,
                    "transaction_type": "DEBIT"
                },
                schema="shared",
                limit=100
            )
            
            # Filter for today's usage
            today_usage = []
            for record in usage_data:
                record_date = datetime.fromisoformat(record.get('created_at', '')).date()
                if record_date == today:
                    today_usage.append(record)
            
            return today_usage
            
        except Exception as e:
            print(f"⚠️ Could not get recent usage: {e}")
            return []
    
    def reserve_credits(self, user_id: str, session_id: str, operation_id: str, 
                       operation_type: str, estimated_tokens: int) -> bool:
        """Reserve credits for an operation atomically"""
        try:
            # Validate operation cost
            validation = self.config.validate_operation_cost(estimated_tokens)
            if not validation["valid"]:
                raise CreditGuardError(validation["reason"])
            
            # Use database function for atomic reservation
            if self.db_client.client:
                result = self.db_client.rpc('reserve_credits', {
                    'p_user_id': user_id,
                    'p_session_id': session_id,
                    'p_operation_id': operation_id,
                    'p_operation_type': operation_type,
                    'p_estimated_tokens': estimated_tokens
                })
                
                return bool(result)
            
            # Fallback to local reservation
            return self._local_reserve_credits(user_id, session_id, operation_id, 
                                             operation_type, estimated_tokens)
            
        except Exception as e:
            print(f"❌ Credit reservation failed: {e}")
            return False
    
    def _local_reserve_credits(self, user_id: str, session_id: str, operation_id: str,
                              operation_type: str, estimated_tokens: int) -> bool:
        """Local fallback for credit reservation"""
        with self._lock:
            # Check availability
            availability = self.check_credit_availability(user_id, estimated_tokens)
            
            if not availability["allowed"]:
                return False
            
            # Create reservation record
            reservation_data = {
                "user_id": user_id,
                "session_id": session_id,
                "task_id": operation_id,
                "operation_type": operation_type,
                "tokens_estimated": estimated_tokens,
                "cost_estimate": estimated_tokens / 1000.0,
                "transaction_type": "DEBIT",
                "metadata": {
                    "reservation": True,
                    "timestamp": datetime.now().isoformat(),
                    "project": self.project_name
                }
            }
            
            # Insert reservation
            result = self.db_client.insert("credit_ledger", reservation_data, "shared")
            return bool(result)
    
    def update_actual_usage(self, operation_id: str, actual_tokens: int, 
                           metadata: Dict[str, Any] = None) -> bool:
        """Update actual token usage for a reserved operation"""
        try:
            # Find the reservation record
            reservations = self.db_client.select(
                table="credit_ledger",
                columns="*",
                filters={
                    "task_id": operation_id,
                    "operation_type": "ESTIMATE"
                },
                schema="shared",
                limit=1
            )
            
            if not reservations:
                print(f"⚠️ No reservation found for operation {operation_id}")
                return False
            
            reservation = reservations[0]
            
            # Update with actual usage
            update_data = {
                "tokens_actual": actual_tokens,
                "cost_actual": actual_tokens / 1000.0,
                "operation_type": "ACTUAL",
                "metadata": {
                    **reservation.get("metadata", {}),
                    **(metadata or {}),
                    "updated_at": datetime.now().isoformat()
                }
            }
            
            success = self.db_client.update(
                table="credit_ledger",
                data=update_data,
                filters={"id": reservation["id"]},
                schema="shared"
            )
            
            return success
            
        except Exception as e:
            print(f"❌ Failed to update actual usage: {e}")
            return False
    
    def refund_credits(self, operation_id: str, reason: str = "operation_cancelled") -> bool:
        """Refund credits for a cancelled operation"""
        try:
            # Find the original transaction
            transactions = self.db_client.select(
                table="credit_ledger",
                columns="*",
                filters={"task_id": operation_id},
                schema="shared"
            )
            
            if not transactions:
                print(f"⚠️ No transaction found for operation {operation_id}")
                return False
            
            original_transaction = transactions[0]
            tokens_to_refund = original_transaction.get("tokens_estimated", 0)
            
            if tokens_to_refund <= 0:
                print(f"⚠️ No tokens to refund for operation {operation_id}")
                return True
            
            # Create refund entry
            refund_data = {
                "user_id": original_transaction["user_id"],
                "session_id": f"refund_{int(time.time())}",
                "task_id": operation_id,
                "operation_type": "REFUND",
                "tokens_estimated": tokens_to_refund,
                "tokens_actual": tokens_to_refund,
                "cost_estimate": tokens_to_refund / 1000.0,
                "cost_actual": tokens_to_refund / 1000.0,
                "transaction_type": "CREDIT",
                "metadata": {
                    "reason": reason,
                    "original_transaction_id": original_transaction["id"],
                    "refunded_tokens": tokens_to_refund,
                    "refund_timestamp": datetime.now().isoformat()
                }
            }
            
            result = self.db_client.insert("credit_ledger", refund_data, "shared")
            return bool(result)
            
        except Exception as e:
            print(f"❌ Credit refund failed: {e}")
            return False
    
    def get_credit_status(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive credit status for user"""
        try:
            # Get current balance from latest transaction
            latest_transactions = self.db_client.select(
                table="credit_ledger",
                columns="remaining_balance, created_at, tokens_actual, operation_type",
                filters={"user_id": user_id},
                schema="shared",
                order_by="-created_at",
                limit=1
            )
            
            if latest_transactions:
                latest = latest_transactions[0]
                current_balance = latest.get("remaining_balance", self.config.credit.daily_limit)
            else:
                current_balance = self.config.credit.daily_limit
            
            # Calculate usage statistics
            daily_limit = self.config.credit.daily_limit
            used_today = daily_limit - current_balance
            usage_percentage = (used_today / daily_limit) * 100
            
            # Get recent activity
            recent_activity = self._get_recent_usage(user_id)
            
            # Calculate statistics
            total_operations = len(recent_activity)
            avg_cost = sum(op.get('tokens_actual', 0) for op in recent_activity) / max(1, total_operations)
            
            return {
                "user_id": user_id,
                "current_balance": current_balance,
                "daily_limit": daily_limit,
                "used_today": used_today,
                "usage_percentage": usage_percentage,
                "warning_threshold": self.config.credit.warning_threshold,
                "emergency_threshold": self.config.credit.emergency_threshold,
                "is_warning": usage_percentage >= (self.config.credit.warning_threshold * 100),
                "is_emergency": usage_percentage >= (self.config.credit.emergency_threshold * 100),
                "operations_today": total_operations,
                "avg_cost_per_operation": avg_cost,
                "last_activity": latest_transactions[0].get("created_at") if latest_transactions else None
            }
            
        except Exception as e:
            print(f"❌ Failed to get credit status: {e}")
            return {
                "user_id": user_id,
                "error": str(e),
                "current_balance": 0,
                "usage_percentage": 100.0
            }
    
    def _rollback_transaction(self, transaction_id: str, reason: str):
        """Rollback a failed transaction"""
        try:
            if transaction_id in self._pending_transactions:
                transaction = self._pending_transactions[transaction_id]
                
                # Create rollback entry if credits were reserved
                if transaction.get("reserved"):
                    self.refund_credits(transaction["operation_id"], f"rollback: {reason}")
                
                # Remove from pending
                del self._pending_transactions[transaction_id]
                
        except Exception as e:
            print(f"⚠️ Rollback failed for transaction {transaction_id}: {e}")
    
    def get_usage_statistics(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get usage statistics for the past N days"""
        try:
            # Get usage data for the specified period
            cutoff_date = datetime.now() - timedelta(days=days)
            
            usage_data = self.db_client.select(
                table="credit_ledger",
                columns="tokens_actual, cost_actual, operation_type, created_at",
                filters={
                    "user_id": user_id,
                    "transaction_type": "DEBIT"
                },
                schema="shared",
                limit=1000
            )
            
            # Filter by date and calculate statistics
            recent_usage = []
            for record in usage_data:
                try:
                    record_date = datetime.fromisoformat(record.get('created_at', ''))
                    if record_date >= cutoff_date:
                        recent_usage.append(record)
                except ValueError:
                    continue
            
            if not recent_usage:
                return {
                    "period_days": days,
                    "total_operations": 0,
                    "total_tokens": 0,
                    "avg_tokens_per_operation": 0,
                    "daily_average": 0
                }
            
            total_tokens = sum(op.get('tokens_actual', 0) for op in recent_usage)
            total_operations = len(recent_usage)
            
            return {
                "period_days": days,
                "total_operations": total_operations,
                "total_tokens": total_tokens,
                "avg_tokens_per_operation": total_tokens / total_operations,
                "daily_average": total_tokens / days,
                "operations_per_day": total_operations / days
            }
            
        except Exception as e:
            print(f"❌ Failed to get usage statistics: {e}")
            return {"error": str(e)}

# Global credit manager instance
_credit_managers = {}

def get_credit_manager(project_name: str = "smart_layer") -> CreditManager:
    """Get a credit manager instance"""
    if project_name not in _credit_managers:
        _credit_managers[project_name] = CreditManager(project_name)
    
    return _credit_managers[project_name]

# Convenience functions
def check_credits(user_id: str, estimated_tokens: int, project_name: str = "smart_layer") -> bool:
    """Quick check if credits are available"""
    manager = get_credit_manager(project_name)
    result = manager.check_credit_availability(user_id, estimated_tokens)
    
    if not result.get("allowed", False):
        print(f"❌ Insufficient credits: {result.get('reason', 'Unknown error')}")
        return False
    
    if result.get("usage_percentage", 0) >= 80:
        print(f"⚠️ High credit usage: {result['usage_percentage']:.1f}%")
    
    return True

def reserve_credits(user_id: str, session_id: str, operation_id: str, 
                   operation_type: str, estimated_tokens: int, 
                   project_name: str = "smart_layer") -> bool:
    """Reserve credits for an operation"""
    manager = get_credit_manager(project_name)
    return manager.reserve_credits(user_id, session_id, operation_id, 
                                 operation_type, estimated_tokens)

def update_credits(operation_id: str, actual_tokens: int, 
                  metadata: Dict[str, Any] = None, 
                  project_name: str = "smart_layer") -> bool:
    """Update actual credit usage"""
    manager = get_credit_manager(project_name)
    return manager.update_actual_usage(operation_id, actual_tokens, metadata)

def refund_credits(operation_id: str, reason: str = "operation_cancelled",
                  project_name: str = "smart_layer") -> bool:
    """Refund credits for cancelled operation"""
    manager = get_credit_manager(project_name)
    return manager.refund_credits(operation_id, reason)

def get_credit_status(user_id: str, project_name: str = "smart_layer") -> Dict[str, Any]:
    """Get credit status for user"""
    manager = get_credit_manager(project_name)
    return manager.get_credit_status(user_id)

if __name__ == "__main__":
    # Test credit management
    manager = get_credit_manager("test_project")
    
    print("💳 Testing Credit Management...")
    
    # Test credit check
    user_id = "test_user"
    availability = manager.check_credit_availability(user_id, 1000)
    print(f"Credit check (1000T): {'✅' if availability.get('allowed') else '❌'}")
    
    # Test reservation
    if availability.get("allowed"):
        reserved = manager.reserve_credits(user_id, "test_session", "test_op", "TEST", 1000)
        print(f"Credit reservation: {'✅' if reserved else '❌'}")
        
        if reserved:
            # Test actual usage update
            updated = manager.update_actual_usage("test_op", 800)
            print(f"Usage update: {'✅' if updated else '❌'}")
    
    # Test status
    status = manager.get_credit_status(user_id)
    print(f"Credit status: {status.get('usage_percentage', 0):.1f}% used")
    
    print("✅ Credit management test complete")

