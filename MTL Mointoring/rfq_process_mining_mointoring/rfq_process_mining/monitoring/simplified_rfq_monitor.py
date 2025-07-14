#!/usr/bin/env python3
"""
Simplified RFQ Process MTL Monitor
=================================

A more direct implementation of MTL monitoring for RFQ process that properly
handles the temporal semantics and business rules.
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Time constants (in seconds)
ONE_DAY = 86400
ONE_WEEK = 604800
THREE_WEEKS = 1814400

@dataclass
class MonitoringResult:
    case_id: str
    property_name: str
    verdict: bool
    timestamp: int
    violation_details: Optional[str] = None

class SimplifiedRFQMonitor:
    """Simplified MTL Monitor for RFQ Process with direct temporal logic evaluation"""
    
    def __init__(self):
        self.case_states = {}
        self.monitoring_results = []
    
    def process_trace(self, trace: Dict[str, Any]) -> List[MonitoringResult]:
        """Process an entire trace and check all MTL properties"""
        case_id = trace['case_id']
        events = trace['events']
        scenario_type = trace.get('scenario_type', 'unknown')
        expected_compliance = trace.get('compliance_status', 'unknown')
        
        print(f"\nProcessing trace: {case_id} ({scenario_type})")
        print(f"Expected compliance: {expected_compliance}")
        
        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda e: e['timestamp'])
        
        # Extract key events and timestamps
        event_map = {}
        for event in sorted_events:
            activity = event['activity']
            timestamp = event['timestamp']
            event_map[activity] = timestamp
        
        results = []
        
        # Check Property 1: Offer Preservation Compliance
        # MTL: G(quotation_sent -> F[0,604800] offer_preserved)
        if 'quotation_sent' in event_map:
            quotation_time = event_map['quotation_sent']
            offer_preserved_time = event_map.get('offer_preserved')
            
            if offer_preserved_time is None:
                # Violation: No offer preservation
                results.append(MonitoringResult(
                    case_id=case_id,
                    property_name="offer_preservation",
                    verdict=False,
                    timestamp=quotation_time,
                    violation_details="Quotation sent but offer never preserved"
                ))
            elif offer_preserved_time - quotation_time > ONE_WEEK:
                # Violation: Offer preserved too late
                results.append(MonitoringResult(
                    case_id=case_id,
                    property_name="offer_preservation",
                    verdict=False,
                    timestamp=offer_preserved_time,
                    violation_details=f"Offer preserved {(offer_preserved_time - quotation_time) / ONE_DAY:.1f} days after quotation (max 7 days)"
                ))
            else:
                # Compliance: Offer preserved within 1 week
                results.append(MonitoringResult(
                    case_id=case_id,
                    property_name="offer_preservation",
                    verdict=True,
                    timestamp=offer_preserved_time,
                    violation_details=None
                ))
        
        # Check Property 2: Purchase Order Timing and Response
        if 'quotation_sent' in event_map and 'po_sent' in event_map:
            quotation_time = event_map['quotation_sent']
            po_time = event_map['po_sent']
            po_accepted_time = event_map.get('po_accepted')
            po_denied_time = event_map.get('po_denied')
            
            days_after_quote = (po_time - quotation_time) / ONE_DAY
            
            if days_after_quote <= 21:
                # PO within deadline - should be accepted
                if po_accepted_time is None:
                    results.append(MonitoringResult(
                        case_id=case_id,
                        property_name="timely_po_response",
                        verdict=False,
                        timestamp=po_time,
                        violation_details=f"PO sent within deadline ({days_after_quote:.1f} days) but not accepted"
                    ))
                elif po_accepted_time - po_time > ONE_DAY:
                    results.append(MonitoringResult(
                        case_id=case_id,
                        property_name="timely_po_response",
                        verdict=False,
                        timestamp=po_accepted_time,
                        violation_details=f"PO accepted too late ({(po_accepted_time - po_time) / ONE_DAY:.1f} days after PO)"
                    ))
                else:
                    results.append(MonitoringResult(
                        case_id=case_id,
                        property_name="timely_po_response",
                        verdict=True,
                        timestamp=po_accepted_time,
                        violation_details=None
                    ))
            else:
                # PO after deadline - should be denied
                if po_denied_time is None:
                    results.append(MonitoringResult(
                        case_id=case_id,
                        property_name="late_po_denial",
                        verdict=False,
                        timestamp=po_time,
                        violation_details=f"PO sent after deadline ({days_after_quote:.1f} days) but not denied"
                    ))
                elif po_denied_time - po_time > ONE_DAY:
                    results.append(MonitoringResult(
                        case_id=case_id,
                        property_name="late_po_denial",
                        verdict=False,
                        timestamp=po_denied_time,
                        violation_details=f"PO denied too late ({(po_denied_time - po_time) / ONE_DAY:.1f} days after PO)"
                    ))
                else:
                    results.append(MonitoringResult(
                        case_id=case_id,
                        property_name="late_po_denial",
                        verdict=True,
                        timestamp=po_denied_time,
                        violation_details=None
                    ))
                
                # Additional check: Late PO should NOT be accepted
                if po_accepted_time is not None:
                    results.append(MonitoringResult(
                        case_id=case_id,
                        property_name="late_po_incorrectly_accepted",
                        verdict=False,
                        timestamp=po_accepted_time,
                        violation_details=f"Late PO ({days_after_quote:.1f} days) incorrectly accepted instead of denied"
                    ))
        
        # Check Property 3: Mutual Exclusion (PO cannot be both accepted and denied)
        if 'po_sent' in event_map:
            po_accepted_time = event_map.get('po_accepted')
            po_denied_time = event_map.get('po_denied')
            
            if po_accepted_time is not None and po_denied_time is not None:
                results.append(MonitoringResult(
                    case_id=case_id,
                    property_name="mutual_exclusion",
                    verdict=False,
                    timestamp=max(po_accepted_time, po_denied_time),
                    violation_details="PO both accepted and denied (mutual exclusion violation)"
                ))
            else:
                results.append(MonitoringResult(
                    case_id=case_id,
                    property_name="mutual_exclusion",
                    verdict=True,
                    timestamp=event_map['po_sent'],
                    violation_details=None
                ))
        
        # Print results for this trace
        for result in results:
            status = "✓ PASS" if result.verdict else "✗ VIOLATION"
            print(f"  {result.property_name}: {status}")
            if not result.verdict and result.violation_details:
                print(f"    Details: {result.violation_details}")
        
        return results
    
    def generate_report(self, all_results: List[MonitoringResult], traces: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive monitoring report"""
        
        # Group results by case
        case_results = {}
        for result in all_results:
            if result.case_id not in case_results:
                case_results[result.case_id] = []
            case_results[result.case_id].append(result)
        
        # Calculate compliance for each case
        case_summaries = []
        total_compliant = 0
        total_violating = 0
        
        property_violation_counts = {
            'offer_preservation': 0,
            'timely_po_response': 0,
            'late_po_denial': 0,
            'late_po_incorrectly_accepted': 0,
            'mutual_exclusion': 0
        }
        
        for trace in traces:
            case_id = trace['case_id']
            expected_compliance = trace.get('compliance_status', 'unknown')
            scenario_type = trace.get('scenario_type', 'unknown')
            
            case_violations = []
            case_passes = []
            
            if case_id in case_results:
                for result in case_results[case_id]:
                    if result.verdict:
                        case_passes.append(result.property_name)
                    else:
                        case_violations.append(result.property_name)
                        if result.property_name in property_violation_counts:
                            property_violation_counts[result.property_name] += 1
            
            is_compliant = len(case_violations) == 0
            
            if is_compliant:
                total_compliant += 1
            else:
                total_violating += 1
            
            case_summaries.append({
                "case_id": case_id,
                "scenario_type": scenario_type,
                "expected_compliance": expected_compliance,
                "actual_compliance": "compliant" if is_compliant else "violating",
                "compliance_match": (expected_compliance == "compliant") == is_compliant,
                "violations": case_violations,
                "passes": case_passes
            })
        
        # Calculate accuracy
        correct_predictions = sum(1 for summary in case_summaries if summary['compliance_match'])
        accuracy = correct_predictions / len(case_summaries) if case_summaries else 0
        
        report = {
            "monitoring_summary": {
                "total_traces": len(traces),
                "compliant_traces": total_compliant,
                "violating_traces": total_violating,
                "compliance_rate": total_compliant / len(traces) if traces else 0,
                "prediction_accuracy": accuracy
            },
            "property_violations": property_violation_counts,
            "case_summaries": case_summaries,
            "detailed_results": [
                {
                    "case_id": r.case_id,
                    "property": r.property_name,
                    "verdict": r.verdict,
                    "timestamp": r.timestamp,
                    "violation_details": r.violation_details
                }
                for r in all_results
            ]
        }
        
        return report

def main():
    """Main function to run simplified RFQ process monitoring"""
    print("=== Simplified RFQ Process MTL Monitoring ===\n")
    
    # Load traces
    log_file = "/home/ubuntu/rfq_process_mining/traces/rfq_event_log.json"
    with open(log_file, 'r') as f:
        log_data = json.load(f)
    
    traces = log_data['traces']
    print(f"Loaded {len(traces)} traces")
    
    # Initialize monitor
    monitor = SimplifiedRFQMonitor()
    
    # Process all traces
    all_results = []
    for trace in traces:
        results = monitor.process_trace(trace)
        all_results.extend(results)
    
    print(f"\n=== Monitoring Complete ===")
    print(f"Processed {len(all_results)} monitoring results")
    
    # Generate report
    report = monitor.generate_report(all_results, traces)
    
    # Save report
    output_file = "/home/ubuntu/rfq_process_mining/results/simplified_monitoring_report.json"
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Results saved to: {output_file}")
    
    # Print summary
    summary = report['monitoring_summary']
    print(f"\n=== Summary ===")
    print(f"Total traces: {summary['total_traces']}")
    print(f"Detected compliant: {summary['compliant_traces']}")
    print(f"Detected violating: {summary['violating_traces']}")
    print(f"Compliance rate: {summary['compliance_rate']:.2%}")
    print(f"Prediction accuracy: {summary['prediction_accuracy']:.2%}")
    
    print(f"\n=== Property Violations ===")
    for prop, count in report['property_violations'].items():
        if count > 0:
            print(f"{prop}: {count} violations")
    
    # Show case-by-case analysis
    print(f"\n=== Case Analysis ===")
    for summary in report['case_summaries']:
        match_status = "✓" if summary['compliance_match'] else "✗"
        print(f"{match_status} {summary['case_id']} ({summary['scenario_type']}): "
              f"Expected {summary['expected_compliance']}, "
              f"Detected {summary['actual_compliance']}")
        if summary['violations']:
            print(f"    Violations: {', '.join(summary['violations'])}")

if __name__ == "__main__":
    main()

