#!/usr/bin/env python3
"""
RFQ Process Trace Generator
==========================

Generates event traces for Request for Quotation (RFQ) process with both
compliant and violating scenarios for MTL monitoring with Reelay.

Business Rules:
1. Supplier must preserve offer for 1 week after quotation
2. PO must be received within 3 weeks of quotation date
3. Late POs must be denied, timely POs must be accepted
"""

import json
import random
import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Time constants (in seconds)
ONE_DAY = 86400
ONE_WEEK = 604800
THREE_WEEKS = 1814400

class EventType(Enum):
    RFQ_SENT = "rfq_sent"
    QUOTATION_PREPARED = "quotation_prepared"
    QUOTATION_SENT = "quotation_sent"
    OFFER_PRESERVED = "offer_preserved"
    PO_SENT = "po_sent"
    PO_ACCEPTED = "po_accepted"
    PO_DENIED = "po_denied"

@dataclass
class Event:
    case_id: str
    activity: str
    timestamp: int
    attributes: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "activity": self.activity,
            "timestamp": self.timestamp,
            "attributes": self.attributes
        }

@dataclass
class Trace:
    case_id: str
    events: List[Event]
    scenario_type: str
    compliance_status: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "scenario_type": self.scenario_type,
            "compliance_status": self.compliance_status,
            "events": [event.to_dict() for event in self.events]
        }

class RFQTraceGenerator:
    def __init__(self, base_timestamp: int = 1640995200):  # 2022-01-01 00:00:00 UTC
        self.base_timestamp = base_timestamp
        self.case_counter = 1
        
    def generate_compliant_traces(self, count: int = 5) -> List[Trace]:
        """Generate compliant traces following business rules"""
        traces = []
        
        # Scenario 1: Perfect compliance - PO within deadline, accepted
        for i in range(count // 3 + 1):
            trace = self._generate_perfect_compliance_trace()
            traces.append(trace)
        
        # Scenario 2: Late PO properly denied
        for i in range(count // 3 + 1):
            trace = self._generate_late_po_denied_trace()
            traces.append(trace)
        
        # Scenario 3: No PO sent (valid scenario)
        for i in range(count // 3):
            trace = self._generate_no_po_trace()
            traces.append(trace)
        
        return traces[:count]
    
    def generate_violating_traces(self, count: int = 5) -> List[Trace]:
        """Generate violating traces that break business rules"""
        traces = []
        
        # Violation 1: Missing offer preservation
        for i in range(count // 4 + 1):
            trace = self._generate_missing_offer_preservation_trace()
            traces.append(trace)
        
        # Violation 2: Late PO incorrectly accepted
        for i in range(count // 4 + 1):
            trace = self._generate_late_po_accepted_trace()
            traces.append(trace)
        
        # Violation 3: No response to timely PO
        for i in range(count // 4 + 1):
            trace = self._generate_no_response_trace()
            traces.append(trace)
        
        # Violation 4: Conflicting responses (both accept and deny)
        for i in range(count // 4):
            trace = self._generate_conflicting_response_trace()
            traces.append(trace)
        
        return traces[:count]
    
    def _get_next_case_id(self) -> str:
        case_id = f"RFQ_{self.case_counter:03d}"
        self.case_counter += 1
        return case_id
    
    def _generate_perfect_compliance_trace(self) -> Trace:
        """Generate a perfectly compliant trace"""
        case_id = self._get_next_case_id()
        events = []
        
        # Start with random offset
        current_time = self.base_timestamp + random.randint(0, ONE_DAY * 30)
        
        # 1. RFQ sent
        events.append(Event(
            case_id=case_id,
            activity=EventType.RFQ_SENT.value,
            timestamp=current_time,
            attributes={
                "company_id": f"COMP_{random.choice(['A', 'B', 'C'])}",
                "supplier_id": f"SUPP_{random.choice(['X', 'Y', 'Z'])}"
            }
        ))
        
        # 2. Quotation prepared (1-3 days later)
        current_time += random.randint(ONE_DAY, 3 * ONE_DAY)
        events.append(Event(
            case_id=case_id,
            activity=EventType.QUOTATION_PREPARED.value,
            timestamp=current_time,
            attributes={
                "quote_id": f"Q_{case_id}",
                "amount": random.randint(10000, 100000)
            }
        ))
        
        # 3. Quotation sent (same day or next day)
        quotation_time = current_time + random.randint(3600, ONE_DAY)
        events.append(Event(
            case_id=case_id,
            activity=EventType.QUOTATION_SENT.value,
            timestamp=quotation_time,
            attributes={
                "quote_date": quotation_time,
                "validity_period": ONE_WEEK
            }
        ))
        
        # 4. Offer preserved (within 1 week)
        preserve_time = quotation_time + random.randint(3600, ONE_WEEK - 3600)
        events.append(Event(
            case_id=case_id,
            activity=EventType.OFFER_PRESERVED.value,
            timestamp=preserve_time,
            attributes={
                "expiry_date": quotation_time + ONE_WEEK,
                "preservation_confirmed": True
            }
        ))
        
        # 5. PO sent (within 3 weeks of quotation)
        po_time = quotation_time + random.randint(ONE_DAY, THREE_WEEKS - ONE_DAY)
        events.append(Event(
            case_id=case_id,
            activity=EventType.PO_SENT.value,
            timestamp=po_time,
            attributes={
                "po_id": f"PO_{case_id}",
                "quote_ref": f"Q_{case_id}",
                "days_after_quote": (po_time - quotation_time) // ONE_DAY
            }
        ))
        
        # 6. PO accepted (within 1 day)
        accept_time = po_time + random.randint(3600, ONE_DAY)
        events.append(Event(
            case_id=case_id,
            activity=EventType.PO_ACCEPTED.value,
            timestamp=accept_time,
            attributes={
                "acceptance_date": accept_time,
                "reason": "PO received within deadline"
            }
        ))
        
        return Trace(
            case_id=case_id,
            events=events,
            scenario_type="perfect_compliance",
            compliance_status="compliant"
        )
    
    def _generate_late_po_denied_trace(self) -> Trace:
        """Generate trace where late PO is properly denied"""
        case_id = self._get_next_case_id()
        events = []
        
        current_time = self.base_timestamp + random.randint(0, ONE_DAY * 30)
        
        # 1. RFQ sent
        events.append(Event(
            case_id=case_id,
            activity=EventType.RFQ_SENT.value,
            timestamp=current_time,
            attributes={
                "company_id": f"COMP_{random.choice(['A', 'B', 'C'])}",
                "supplier_id": f"SUPP_{random.choice(['X', 'Y', 'Z'])}"
            }
        ))
        
        # 2. Quotation prepared
        current_time += random.randint(ONE_DAY, 3 * ONE_DAY)
        events.append(Event(
            case_id=case_id,
            activity=EventType.QUOTATION_PREPARED.value,
            timestamp=current_time,
            attributes={
                "quote_id": f"Q_{case_id}",
                "amount": random.randint(10000, 100000)
            }
        ))
        
        # 3. Quotation sent
        quotation_time = current_time + random.randint(3600, ONE_DAY)
        events.append(Event(
            case_id=case_id,
            activity=EventType.QUOTATION_SENT.value,
            timestamp=quotation_time,
            attributes={
                "quote_date": quotation_time,
                "validity_period": ONE_WEEK
            }
        ))
        
        # 4. Offer preserved
        preserve_time = quotation_time + random.randint(3600, ONE_WEEK - 3600)
        events.append(Event(
            case_id=case_id,
            activity=EventType.OFFER_PRESERVED.value,
            timestamp=preserve_time,
            attributes={
                "expiry_date": quotation_time + ONE_WEEK,
                "preservation_confirmed": True
            }
        ))
        
        # 5. PO sent AFTER 3 weeks (late)
        po_time = quotation_time + THREE_WEEKS + random.randint(ONE_DAY, ONE_WEEK)
        events.append(Event(
            case_id=case_id,
            activity=EventType.PO_SENT.value,
            timestamp=po_time,
            attributes={
                "po_id": f"PO_{case_id}",
                "quote_ref": f"Q_{case_id}",
                "days_after_quote": (po_time - quotation_time) // ONE_DAY
            }
        ))
        
        # 6. PO denied (correct response for late PO)
        deny_time = po_time + random.randint(3600, ONE_DAY)
        events.append(Event(
            case_id=case_id,
            activity=EventType.PO_DENIED.value,
            timestamp=deny_time,
            attributes={
                "denial_date": deny_time,
                "reason": "PO received after 3-week deadline"
            }
        ))
        
        return Trace(
            case_id=case_id,
            events=events,
            scenario_type="late_po_denied",
            compliance_status="compliant"
        )
    
    def _generate_no_po_trace(self) -> Trace:
        """Generate trace where no PO is sent (valid scenario)"""
        case_id = self._get_next_case_id()
        events = []
        
        current_time = self.base_timestamp + random.randint(0, ONE_DAY * 30)
        
        # 1. RFQ sent
        events.append(Event(
            case_id=case_id,
            activity=EventType.RFQ_SENT.value,
            timestamp=current_time,
            attributes={
                "company_id": f"COMP_{random.choice(['A', 'B', 'C'])}",
                "supplier_id": f"SUPP_{random.choice(['X', 'Y', 'Z'])}"
            }
        ))
        
        # 2. Quotation prepared
        current_time += random.randint(ONE_DAY, 3 * ONE_DAY)
        events.append(Event(
            case_id=case_id,
            activity=EventType.QUOTATION_PREPARED.value,
            timestamp=current_time,
            attributes={
                "quote_id": f"Q_{case_id}",
                "amount": random.randint(10000, 100000)
            }
        ))
        
        # 3. Quotation sent
        quotation_time = current_time + random.randint(3600, ONE_DAY)
        events.append(Event(
            case_id=case_id,
            activity=EventType.QUOTATION_SENT.value,
            timestamp=quotation_time,
            attributes={
                "quote_date": quotation_time,
                "validity_period": ONE_WEEK
            }
        ))
        
        # 4. Offer preserved
        preserve_time = quotation_time + random.randint(3600, ONE_WEEK - 3600)
        events.append(Event(
            case_id=case_id,
            activity=EventType.OFFER_PRESERVED.value,
            timestamp=preserve_time,
            attributes={
                "expiry_date": quotation_time + ONE_WEEK,
                "preservation_confirmed": True
            }
        ))
        
        # No PO sent - company decided not to proceed
        
        return Trace(
            case_id=case_id,
            events=events,
            scenario_type="no_po_sent",
            compliance_status="compliant"
        )
    
    def _generate_missing_offer_preservation_trace(self) -> Trace:
        """Generate trace missing offer preservation (violation)"""
        case_id = self._get_next_case_id()
        events = []
        
        current_time = self.base_timestamp + random.randint(0, ONE_DAY * 30)
        
        # 1. RFQ sent
        events.append(Event(
            case_id=case_id,
            activity=EventType.RFQ_SENT.value,
            timestamp=current_time,
            attributes={
                "company_id": f"COMP_{random.choice(['A', 'B', 'C'])}",
                "supplier_id": f"SUPP_{random.choice(['X', 'Y', 'Z'])}"
            }
        ))
        
        # 2. Quotation prepared
        current_time += random.randint(ONE_DAY, 3 * ONE_DAY)
        events.append(Event(
            case_id=case_id,
            activity=EventType.QUOTATION_PREPARED.value,
            timestamp=current_time,
            attributes={
                "quote_id": f"Q_{case_id}",
                "amount": random.randint(10000, 100000)
            }
        ))
        
        # 3. Quotation sent
        quotation_time = current_time + random.randint(3600, ONE_DAY)
        events.append(Event(
            case_id=case_id,
            activity=EventType.QUOTATION_SENT.value,
            timestamp=quotation_time,
            attributes={
                "quote_date": quotation_time,
                "validity_period": ONE_WEEK
            }
        ))
        
        # 4. NO offer preservation (VIOLATION)
        
        # 5. PO sent within deadline
        po_time = quotation_time + random.randint(ONE_DAY, THREE_WEEKS - ONE_DAY)
        events.append(Event(
            case_id=case_id,
            activity=EventType.PO_SENT.value,
            timestamp=po_time,
            attributes={
                "po_id": f"PO_{case_id}",
                "quote_ref": f"Q_{case_id}",
                "days_after_quote": (po_time - quotation_time) // ONE_DAY
            }
        ))
        
        # 6. PO accepted (but offer was never preserved)
        accept_time = po_time + random.randint(3600, ONE_DAY)
        events.append(Event(
            case_id=case_id,
            activity=EventType.PO_ACCEPTED.value,
            timestamp=accept_time,
            attributes={
                "acceptance_date": accept_time,
                "reason": "PO accepted without proper offer preservation"
            }
        ))
        
        return Trace(
            case_id=case_id,
            events=events,
            scenario_type="missing_offer_preservation",
            compliance_status="violating"
        )
    
    def _generate_late_po_accepted_trace(self) -> Trace:
        """Generate trace where late PO is incorrectly accepted (violation)"""
        case_id = self._get_next_case_id()
        events = []
        
        current_time = self.base_timestamp + random.randint(0, ONE_DAY * 30)
        
        # Standard beginning
        events.append(Event(
            case_id=case_id,
            activity=EventType.RFQ_SENT.value,
            timestamp=current_time,
            attributes={
                "company_id": f"COMP_{random.choice(['A', 'B', 'C'])}",
                "supplier_id": f"SUPP_{random.choice(['X', 'Y', 'Z'])}"
            }
        ))
        
        current_time += random.randint(ONE_DAY, 3 * ONE_DAY)
        events.append(Event(
            case_id=case_id,
            activity=EventType.QUOTATION_PREPARED.value,
            timestamp=current_time,
            attributes={
                "quote_id": f"Q_{case_id}",
                "amount": random.randint(10000, 100000)
            }
        ))
        
        quotation_time = current_time + random.randint(3600, ONE_DAY)
        events.append(Event(
            case_id=case_id,
            activity=EventType.QUOTATION_SENT.value,
            timestamp=quotation_time,
            attributes={
                "quote_date": quotation_time,
                "validity_period": ONE_WEEK
            }
        ))
        
        preserve_time = quotation_time + random.randint(3600, ONE_WEEK - 3600)
        events.append(Event(
            case_id=case_id,
            activity=EventType.OFFER_PRESERVED.value,
            timestamp=preserve_time,
            attributes={
                "expiry_date": quotation_time + ONE_WEEK,
                "preservation_confirmed": True
            }
        ))
        
        # PO sent AFTER 3 weeks (late)
        po_time = quotation_time + THREE_WEEKS + random.randint(ONE_DAY, ONE_WEEK)
        events.append(Event(
            case_id=case_id,
            activity=EventType.PO_SENT.value,
            timestamp=po_time,
            attributes={
                "po_id": f"PO_{case_id}",
                "quote_ref": f"Q_{case_id}",
                "days_after_quote": (po_time - quotation_time) // ONE_DAY
            }
        ))
        
        # PO ACCEPTED (VIOLATION - should be denied)
        accept_time = po_time + random.randint(3600, ONE_DAY)
        events.append(Event(
            case_id=case_id,
            activity=EventType.PO_ACCEPTED.value,
            timestamp=accept_time,
            attributes={
                "acceptance_date": accept_time,
                "reason": "Incorrectly accepted late PO"
            }
        ))
        
        return Trace(
            case_id=case_id,
            events=events,
            scenario_type="late_po_accepted",
            compliance_status="violating"
        )
    
    def _generate_no_response_trace(self) -> Trace:
        """Generate trace with no response to PO (violation)"""
        case_id = self._get_next_case_id()
        events = []
        
        current_time = self.base_timestamp + random.randint(0, ONE_DAY * 30)
        
        # Standard beginning through PO
        events.append(Event(
            case_id=case_id,
            activity=EventType.RFQ_SENT.value,
            timestamp=current_time,
            attributes={
                "company_id": f"COMP_{random.choice(['A', 'B', 'C'])}",
                "supplier_id": f"SUPP_{random.choice(['X', 'Y', 'Z'])}"
            }
        ))
        
        current_time += random.randint(ONE_DAY, 3 * ONE_DAY)
        events.append(Event(
            case_id=case_id,
            activity=EventType.QUOTATION_PREPARED.value,
            timestamp=current_time,
            attributes={
                "quote_id": f"Q_{case_id}",
                "amount": random.randint(10000, 100000)
            }
        ))
        
        quotation_time = current_time + random.randint(3600, ONE_DAY)
        events.append(Event(
            case_id=case_id,
            activity=EventType.QUOTATION_SENT.value,
            timestamp=quotation_time,
            attributes={
                "quote_date": quotation_time,
                "validity_period": ONE_WEEK
            }
        ))
        
        preserve_time = quotation_time + random.randint(3600, ONE_WEEK - 3600)
        events.append(Event(
            case_id=case_id,
            activity=EventType.OFFER_PRESERVED.value,
            timestamp=preserve_time,
            attributes={
                "expiry_date": quotation_time + ONE_WEEK,
                "preservation_confirmed": True
            }
        ))
        
        # PO sent within deadline
        po_time = quotation_time + random.randint(ONE_DAY, THREE_WEEKS - ONE_DAY)
        events.append(Event(
            case_id=case_id,
            activity=EventType.PO_SENT.value,
            timestamp=po_time,
            attributes={
                "po_id": f"PO_{case_id}",
                "quote_ref": f"Q_{case_id}",
                "days_after_quote": (po_time - quotation_time) // ONE_DAY
            }
        ))
        
        # NO RESPONSE (VIOLATION - should accept within 1 day)
        
        return Trace(
            case_id=case_id,
            events=events,
            scenario_type="no_response_to_po",
            compliance_status="violating"
        )
    
    def _generate_conflicting_response_trace(self) -> Trace:
        """Generate trace with both accept and deny (violation)"""
        case_id = self._get_next_case_id()
        events = []
        
        current_time = self.base_timestamp + random.randint(0, ONE_DAY * 30)
        
        # Standard beginning through PO
        events.append(Event(
            case_id=case_id,
            activity=EventType.RFQ_SENT.value,
            timestamp=current_time,
            attributes={
                "company_id": f"COMP_{random.choice(['A', 'B', 'C'])}",
                "supplier_id": f"SUPP_{random.choice(['X', 'Y', 'Z'])}"
            }
        ))
        
        current_time += random.randint(ONE_DAY, 3 * ONE_DAY)
        events.append(Event(
            case_id=case_id,
            activity=EventType.QUOTATION_PREPARED.value,
            timestamp=current_time,
            attributes={
                "quote_id": f"Q_{case_id}",
                "amount": random.randint(10000, 100000)
            }
        ))
        
        quotation_time = current_time + random.randint(3600, ONE_DAY)
        events.append(Event(
            case_id=case_id,
            activity=EventType.QUOTATION_SENT.value,
            timestamp=quotation_time,
            attributes={
                "quote_date": quotation_time,
                "validity_period": ONE_WEEK
            }
        ))
        
        preserve_time = quotation_time + random.randint(3600, ONE_WEEK - 3600)
        events.append(Event(
            case_id=case_id,
            activity=EventType.OFFER_PRESERVED.value,
            timestamp=preserve_time,
            attributes={
                "expiry_date": quotation_time + ONE_WEEK,
                "preservation_confirmed": True
            }
        ))
        
        po_time = quotation_time + random.randint(ONE_DAY, THREE_WEEKS - ONE_DAY)
        events.append(Event(
            case_id=case_id,
            activity=EventType.PO_SENT.value,
            timestamp=po_time,
            attributes={
                "po_id": f"PO_{case_id}",
                "quote_ref": f"Q_{case_id}",
                "days_after_quote": (po_time - quotation_time) // ONE_DAY
            }
        ))
        
        # BOTH accept and deny (VIOLATION)
        accept_time = po_time + random.randint(3600, ONE_DAY // 2)
        events.append(Event(
            case_id=case_id,
            activity=EventType.PO_ACCEPTED.value,
            timestamp=accept_time,
            attributes={
                "acceptance_date": accept_time,
                "reason": "Initial acceptance"
            }
        ))
        
        deny_time = accept_time + random.randint(3600, ONE_DAY // 2)
        events.append(Event(
            case_id=case_id,
            activity=EventType.PO_DENIED.value,
            timestamp=deny_time,
            attributes={
                "denial_date": deny_time,
                "reason": "Conflicting denial after acceptance"
            }
        ))
        
        return Trace(
            case_id=case_id,
            events=events,
            scenario_type="conflicting_responses",
            compliance_status="violating"
        )

def main():
    """Generate and save traces for RFQ process monitoring"""
    generator = RFQTraceGenerator()
    
    print("Generating RFQ process traces...")
    
    # Generate compliant traces
    compliant_traces = generator.generate_compliant_traces(6)
    print(f"Generated {len(compliant_traces)} compliant traces")
    
    # Generate violating traces
    violating_traces = generator.generate_violating_traces(8)
    print(f"Generated {len(violating_traces)} violating traces")
    
    # Save traces
    all_traces = compliant_traces + violating_traces
    
    # Save individual trace files
    for trace in all_traces:
        filename = f"/home/ubuntu/rfq_process_mining/traces/{trace.case_id}_{trace.scenario_type}.json"
        with open(filename, 'w') as f:
            json.dump(trace.to_dict(), f, indent=2)
    
    # Save combined log file
    log_data = {
        "metadata": {
            "total_traces": len(all_traces),
            "compliant_traces": len(compliant_traces),
            "violating_traces": len(violating_traces),
            "generation_timestamp": datetime.datetime.now().isoformat()
        },
        "traces": [trace.to_dict() for trace in all_traces]
    }
    
    with open("/home/ubuntu/rfq_process_mining/traces/rfq_event_log.json", 'w') as f:
        json.dump(log_data, f, indent=2)
    
    # Generate summary
    print("\n=== Trace Generation Summary ===")
    print(f"Total traces: {len(all_traces)}")
    print(f"Compliant: {len(compliant_traces)}")
    print(f"Violating: {len(violating_traces)}")
    
    print("\nCompliant scenarios:")
    for trace in compliant_traces:
        print(f"  - {trace.case_id}: {trace.scenario_type}")
    
    print("\nViolating scenarios:")
    for trace in violating_traces:
        print(f"  - {trace.case_id}: {trace.scenario_type}")
    
    print(f"\nTraces saved to: /home/ubuntu/rfq_process_mining/traces/")

if __name__ == "__main__":
    main()

