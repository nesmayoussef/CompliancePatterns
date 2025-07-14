#!/usr/bin/env python3
"""
RFQ Process MTL Monitor with W_Nabellen -> A_ACCEPTED Chain Precedence
======================================================================
"""

import json
import time
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
import mtl

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


class RFQMTLMonitor:
    """MTL Monitor with W_Nabellen -> A_ACCEPTED chain precedence"""

    def __init__(self):
        self.case_states = {}
        self.monitoring_results = []
        self.response_time_limit = ONE_WEEK
        self.setup_mtl_properties()

    def setup_mtl_properties(self):
        """Define MTL properties including Chain Precedence"""
        # Existing response property
        self.a_submitted = mtl.parse('a_submitted')
        self.w_complete = mtl.parse('w_completeren_aanvraag')
        self.response_property = (
            self.a_submitted.implies(
                self.w_complete.eventually()
            )
        ).always()
        self.a_accepted = mtl.parse('a_accepted')
        self.w_nabellen = mtl.parse('w_nabellen_offertes')
        self.a_preaccepted = mtl.parse('a_preaccepted')
        # Timed response: A_ACCEPTED must be followed by W_Nabellen within 5 seconds
        self.timed_response_property = (
            self.a_accepted.implies(
                self.w_nabellen.eventually(lo=0, hi=5000)  # 5000 ms = 5 seconds
            )
        ).always()

        response_condition = self.a_preaccepted

        # The pattern means:
        # After a_submitted, no other a_submitted occurs until response_condition happens
        # We can express this as:
        # a_submitted implies that eventually response_condition will happen,
        # and until then, no a_submitted occurs
        self.alternate_response_property = (
            self.a_submitted.implies(
                (~self.a_submitted).until(response_condition)
            )
        ).always()

        self.strict_chain_response = (
            self.a_accepted.implies(
                mtl.And([
                    mtl.Next(self.w_complete),  # Immediate next event
                    self.w_complete.eventually(lo=0, hi= 5000)  # Within 5 seconds
                ])
            )
        ).always()

         # Runtime tracking configuration
        self.use_mtl_strict_chain = False  # Set True to use MTL evaluation

        # Absence pattern: A_FINALIZED should never occur
        self.a_finalized = mtl.parse('a_finalized')
        self.absence_property = (~self.a_finalized).always(lo=0, hi= 5000)

        # Add manual tracking flag
        self.track_absence_manually = True  # Configurable approach

        self.o_declined = mtl.parse('a_declined')
        self.existence_property = self.o_declined.eventually(lo=0, hi= 5000)

    def _update_signals(self, case_id: str, event: Dict[str, Any]):
        """Update MTL signals including new signals for strict chain"""
        case_state = self.case_states[case_id]
        signals = case_state['signals']
        activity = event['activity']
        timestamp = event['timestamp']
        # Reset all signals to False for this timestamp
        for signal_name in signals:
            signals[signal_name].append((timestamp, False))

        # New signal updates for strict chain
        if activity == 'a_accepted':
            signals['a_accepted'][-1] = (timestamp, True)
        elif activity == 'w_completeren_aanvraag':
            signals['w_completeren_aanvraag'][-1] = (timestamp, True)

    def process_event(self, event: Dict[str, Any]) -> List[MonitoringResult]:
        """Process a single event and update monitoring state"""
        case_id = event['case_id']
        activity = event['activity']
        timestamp = event['timestamp']
        if case_id not in self.case_states:
            self.case_states[case_id] = {
                'events': [],
                'a_submitted_time': None,
                'w_complete_time': None,
                'violation_reported': False,
                'completed': False,
                'last_event': None,
                'chain_precede_violations': set(),
                'pending_alternate_response': False,  # For alternate response
                'seen_intermediate_submit': False,  # For alternate response
                'expecting_w_complete': None,  # For strict chain tracking
            }

        case_state = self.case_states[case_id]
        case_state['events'].append(event)

        # Check all patterns
        chain_results = self._check_chain_precede(case_id, activity, timestamp, case_state)
        response_results = self._check_response_pattern(case_id, activity, timestamp, case_state)
        alternate_results = self._check_alternate_response(case_id, activity, timestamp, case_state)
        strict_chain_results = self._check_strict_chain_response(case_id, activity, timestamp, case_state)
        # Check absence patterns
        absence_results = self._check_absence_patterns(case_id, activity, timestamp, case_state)
        existence_results = self._check_existence_patterns(case_id, activity, timestamp, case_state)
        # Update last event
        case_state['last_event'] = activity


        results = strict_chain_results + chain_results + response_results + alternate_results + absence_results + existence_results
        self.monitoring_results.extend(results)
        return results

  
    def _check_absence_patterns(self, case_id, activity, timestamp, case_state):
        results = []

        if activity.upper() == 'A_FINALIZED':
            # Manual tracking
            if self.track_absence_manually:
                results.append(MonitoringResult(
                    case_id=case_id,
                    property_name="absence_a_finalized",
                    verdict=False,
                    timestamp=timestamp,
                    violation_details="Violation: A_FINALIZED occurred when forbidden"
                ))

            # MTL-based tracking
            case_state['a_finalized_occurred'] = True

        return results
    def _check_response_pattern(self, case_id: str, activity: str, timestamp: int,
                                case_state: Dict[str, Any]) -> List[MonitoringResult]:
        """Check response pattern compliance"""
        results = []

        if activity == 'a_submitted' and case_state['a_submitted_time'] is None:
            case_state['a_submitted_time'] = timestamp
        elif activity == 'w_completeren_aanvraag':
            case_state['w_complete_time'] = timestamp
            case_state['completed'] = True

        if case_state['a_submitted_time'] is not None:
            submitted_time = case_state['a_submitted_time']

            if case_state['completed']:
                results.append(MonitoringResult(
                    case_id=case_id,
                    property_name="response",
                    verdict=True,
                    timestamp=case_state['w_complete_time'],
                    violation_details=f"Compliant: completed after {case_state['w_complete_time'] - submitted_time}s"
                ))
            elif (timestamp >= (submitted_time + self.response_time_limit) and
                  not case_state['violation_reported']):
                results.append(MonitoringResult(
                    case_id=case_id,
                    property_name="response",
                    verdict=False,
                    timestamp=submitted_time + self.response_time_limit,
                    violation_details="Violation: No completion within deadline"
                ))
                case_state['violation_reported'] = True

        return results

    def _check_existence_patterns(self, case_id: str, activity: str,
                                  timestamp: int, case_state: Dict[str, Any]) -> List[MonitoringResult]:
        results = []

        # Initialize 'a_declined_found' if not already set
        if 'a_declined_found' not in case_state:
            case_state['a_declined_found'] = False
          

        # Check if current activity is 'A_DECLINED'
        if activity.upper() == 'A_DECLINED':
            case_state['a_declined_found'] = True

           
        return results
    def _check_chain_precede(self, case_id: str, activity: str, timestamp: int,
                             case_state: Dict[str, Any]) -> List[MonitoringResult]:
        """Hybrid check using both MTL and manual tracking"""
        results = []

        if activity == self.w_nabellen:
            # Get the history of events
            events = case_state['events']

            # Find all A_ACCEPTED events that could precede this W_Nabellen
            a_accepted_events = [
                e for e in events
                if e['activity'] == self.a_accepted
                   and e['timestamp'] < timestamp
            ]

            # Find all W_Nabellen events before this one
            previous_nabellen = [
                e for e in events
                if e['activity'] == self.w_nabellen
                   and e['timestamp'] < timestamp
            ]

            # The valid A_ACCEPTED must be after the last W_Nabellen
            last_nabellen_time = max([e['timestamp'] for e in previous_nabellen]) if previous_nabellen else 0

            # Check if there's an A_ACCEPTED between last W_Nabellen and current W_Nabellen
            valid_accept = any(
                e['timestamp'] > last_nabellen_time
                for e in a_accepted_events
            )

            if not valid_accept:
                violation_msg = (
                    "Violation: W_Nabellen at {} not properly preceded by A_ACCEPTED. "
                    "Last W_Nabellen was at {}, no A_ACCEPTED in between".format(
                        timestamp,
                        last_nabellen_time if previous_nabellen else "never"
                    )
                )

                if timestamp not in case_state['chain_precede_violations']:
                    results.append(MonitoringResult(
                        case_id=case_id,
                        property_name="chain_precede",
                        verdict=False,
                        timestamp=timestamp,
                        violation_details=violation_msg
                    ))
                    case_state['chain_precede_violations'].add(timestamp)

        return results

    def _check_chain_precede_within_Timeframe(self, case_id: str, activity: str, timestamp: int,
                             case_state: Dict[str, Any]) -> List[MonitoringResult]:
        """Check chain precedence with 5-second timeframe requirement"""
        results = []
        MAX_TIME_GAP = 5  # 5-second maximum allowed gap

        if activity == self.w_nabellen:
            # Get the history of events
            events = case_state['events']

            # Find all A_ACCEPTED events that could precede this W_Nabellen
            a_accepted_events = [
                e for e in events
                if e['activity'] == self.a_accepted
                   and e['timestamp'] < timestamp
            ]

            # Find all W_Nabellen events before this one
            previous_nabellen = [
                e for e in events
                if e['activity'] == self.w_nabellen
                   and e['timestamp'] < timestamp
            ]

            # The valid A_ACCEPTED must be after the last W_Nabellen
            last_nabellen_time = max([e['timestamp'] for e in previous_nabellen]) if previous_nabellen else 0

            # Find all A_ACCEPTED events between last W_Nabellen and current W_Nabellen
            valid_accepts = [
                e for e in a_accepted_events
                if e['timestamp'] > last_nabellen_time
            ]

            if not valid_accepts:
                # No A_ACCEPTED between last W_Nabellen and current one
                violation_msg = (
                    "Violation: W_Nabellen at {} not properly preceded by A_ACCEPTED. "
                    "Last W_Nabellen was at {}, no A_ACCEPTED in between".format(
                        timestamp,
                        last_nabellen_time if previous_nabellen else "never"
                    )
                )

                if timestamp not in case_state['chain_precede_violations']:
                    results.append(MonitoringResult(
                        case_id=case_id,
                        property_name="chain_precede",
                        verdict=False,
                        timestamp=timestamp,
                        violation_details=violation_msg
                    ))
                    case_state['chain_precede_violations'].add(timestamp)
            else:
                # Check if the most recent A_ACCEPTED is within 5 seconds of this W_Nabellen
                most_recent_accept = max(valid_accepts, key=lambda x: x['timestamp'])
                time_gap = timestamp - most_recent_accept['timestamp']

                if time_gap > MAX_TIME_GAP:
                    violation_msg = (
                        "Violation: W_Nabellen at {} occurred {} seconds after A_ACCEPTED, "
                        "exceeding maximum allowed gap of {} seconds".format(
                            timestamp,
                            time_gap,
                            MAX_TIME_GAP
                        )
                    )

                    if timestamp not in case_state['chain_precede_violations']:
                        results.append(MonitoringResult(
                            case_id=case_id,
                            property_name="chain_precede_timeframe",
                            verdict=False,
                            timestamp=timestamp,
                            violation_details=violation_msg
                        ))
                        case_state['chain_precede_violations'].add(timestamp)

        return results
    def _check_alternate_response(self, case_id: str, activity: str, timestamp: int,
                                  case_state: Dict[str, Any]) -> List[MonitoringResult]:
        results = []

        if activity == 'a_submitted':
            if not case_state.get('pending_alternate_response', False):
                # Start tracking only if not already pending
                case_state['pending_alternate_response'] = True
                case_state['seen_intermediate_submit'] = False
                case_state['last_submitted_time'] = timestamp
            else:
                # Intermediate submit while waiting for response = violation
                case_state['seen_intermediate_submit'] = True

        elif activity in ('a_preaccepted', 'w_completeren_aanvraag'):
            if case_state.get('pending_alternate_response', False):
                if case_state.get('seen_intermediate_submit', False):
                    # Violation: Intermediate submit occurred
                    results.append(MonitoringResult(
                        case_id=case_id,
                        property_name="alternate_response",
                        verdict=False,
                        timestamp=timestamp,
                        violation_details=f"Violation: {activity} follows intermediate a_submitted"
                    ))
                else:
                    # Valid response
                    results.append(MonitoringResult(
                        case_id=case_id,
                        property_name="alternate_response",
                        verdict=True,
                        timestamp=timestamp
                    ))
                case_state['pending_alternate_response'] = False  # Reset

        return results

    def _check_alternate_response_within_timeframe(self, case_id: str, activity: str, timestamp: int,
                                  case_state: Dict[str, Any]) -> List[MonitoringResult]:
        """Check alternate response pattern with 5-second timeframe requirement"""
        results = []
        RESPONSE_TIMEOUT = 5  # 5-second response timeframe

        if activity == 'a_submitted':
            if not case_state.get('pending_alternate_response', False):
                # Start tracking only if not already pending
                case_state['pending_alternate_response'] = True
                case_state['seen_intermediate_submit'] = False
                case_state['last_submitted_time'] = timestamp
                case_state['response_deadline'] = timestamp + RESPONSE_TIMEOUT
            else:
                # Intermediate submit while waiting for response = violation
                case_state['seen_intermediate_submit'] = True
                # Update the deadline for the new submission
                case_state['response_deadline'] = timestamp + RESPONSE_TIMEOUT

        elif activity in ('a_preaccepted', 'w_completeren_aanvraag'):
            if case_state.get('pending_alternate_response', False):
                # Check if response is within timeframe
                time_since_submit = timestamp - case_state['last_submitted_time']
                within_timeframe = time_since_submit <= RESPONSE_TIMEOUT

                if case_state.get('seen_intermediate_submit', False):
                    # Violation: Intermediate submit occurred
                    results.append(MonitoringResult(
                        case_id=case_id,
                        property_name="alternate_response",
                        verdict=False,
                        timestamp=timestamp,
                        violation_details=f"Violation: {activity} follows intermediate a_submitted"
                    ))
                elif not within_timeframe:
                    # Violation: Response received but too late
                    results.append(MonitoringResult(
                        case_id=case_id,
                        property_name="alternate_response_timeframe",
                        verdict=False,
                        timestamp=case_state['response_deadline'],
                        violation_details=(
                            f"Violation: Response {activity} received {time_since_submit} seconds "
                            f"after a_submitted (exceeds {RESPONSE_TIMEOUT}s limit)"
                        )
                    ))
                else:
                    # Valid response within timeframe
                    results.append(MonitoringResult(
                        case_id=case_id,
                        property_name="alternate_response",
                        verdict=True,
                        timestamp=timestamp,
                        violation_details=(
                            f"Valid response received {time_since_submit} seconds "
                            f"after a_submitted (within {RESPONSE_TIMEOUT}s limit)"
                        )
                    ))
                case_state['pending_alternate_response'] = False  # Reset

        # Check for timeout violations
        if (case_state.get('pending_alternate_response', False) and
                timestamp >= case_state.get('response_deadline', float('inf'))):
            time_since_submit = timestamp - case_state['last_submitted_time']
            results.append(MonitoringResult(
                case_id=case_id,
                property_name="alternate_response_timeframe",
                verdict=False,
                timestamp=case_state['response_deadline'],
                violation_details=(
                    f"Violation: No response received within {RESPONSE_TIMEOUT} seconds "
                    f"of a_submitted (waited {time_since_submit}s)"
                )
            ))
            case_state['pending_alternate_response'] = False  # Reset after timeout

        return results
   

    def _check_strict_chain_response(self, case_id: str, activity: str,
                                     timestamp: int, case_state: Dict[str, Any]) -> List[MonitoringResult]:
        results = []

        if activity.upper() == 'A_ACCEPTED':
            # When we see A_ACCEPTED, check if there was a recent w_completeren_aanvraag
            events = case_state['events']
            current_position = len(events)

            # Look for the most recent w_completeren_aanvraag before this position
            last_complete_pos = None
            for i in range(current_position - 1, -1, -1):
                if events[i]['activity'].lower() == 'w_completeren_aanvraag':
                    last_complete_pos = i
                    break

            if last_complete_pos is not None and last_complete_pos != current_position - 1:
                # Found w_completeren_aanvraag, but not immediately before
                intermediate_events = events[last_complete_pos + 1:current_position]
                intermediate_activities = [e['activity'] for e in intermediate_events]

                results.append(MonitoringResult(
                    case_id=case_id,
                    property_name="strict_chain_response",
                    verdict=False,
                    timestamp=timestamp,
                    violation_details=(
                        f"Violation: w_completeren_aanvraag at position {last_complete_pos} "
                        f"not immediately before A_ACCEPTED. Intermediate events: {intermediate_activities}"
                    )
                ))
                print(f"STRICT CHAIN VIOLATION: {results[-1].violation_details}")

        return results
    #

   
    def process_trace(self, trace: Dict[str, Any]) -> List[MonitoringResult]:
        """Process an entire trace"""
        case_id = trace['case_id']
        events = trace['events']
        all_results = []

        for event in sorted(events, key=lambda e: e['timestamp']):
            results = self.process_event(event)
            all_results.extend(results)

        # Final checks
        case_state = self.case_states.get(case_id, {})

        # Response pattern final check
        if (case_state.get('a_submitted_time') is not None and
                not case_state.get('completed') and
                not case_state.get('violation_reported')):
            violation = MonitoringResult(
                case_id=case_id,
                property_name="response",
                verdict=False,
                timestamp=case_state['a_submitted_time'] + self.response_time_limit,
                violation_details="Final Violation: Trace ended without completion"
            )
            all_results.append(violation)
            print(f"  Response pattern: ✗ VIOLATION (never completed)")

        # Alternate Response final check
        if (case_state.get('pending_alternate_response', False) and
                not any(r.property_name == "alternate_response" and r.verdict
                        for r in all_results)):
            violation_msg = "Final Violation: No valid response after a_submitted"
            all_results.append(MonitoringResult(
                case_id=case_id,
                property_name="alternate_response",
                verdict=False,
                timestamp=case_state['last_submitted_time'],
                violation_details=violation_msg
            ))

        # Chain Precede summary
        chain_violations = [r for r in all_results if r.property_name == "chain_precede"]
        if chain_violations:
            print(f"  Chain Precede: ✗ VIOLATION ({len(chain_violations)} violations)")
        else:
            print("  Chain Precede: ✓ COMPLIANT")

        # Strict Chain Response summary
        strict_chain_violations = [r for r in all_results
                                   if r.property_name == "strict_chain_response" and not r.verdict]
        if strict_chain_violations:
            print(f"  Strict Chain Response: ✗ VIOLATION ({len(strict_chain_violations)} violations)")
            for violation in strict_chain_violations:
                print(f"    - {violation.violation_details}")
        else:
            print("  Strict Chain Response: ✓ COMPLIANT")

       
        if case_state.get('a_finalized_occurred', False):
            print("MTL violation detected: A_FINALIZED occurred")
                   # SINGLE authoritative existence check

        if not case_state.get('a_declined_found', False):
            all_results.append(MonitoringResult(
                case_id=case_id,
                property_name="existence_o_declined",
                verdict=False,
                timestamp=trace['events'][-1]['timestamp'],
                violation_details="Violation: O_DECLINED was never found in this case"
            ))

        return all_results

    def get_case_summary(self, case_id: str) -> Dict[str, Any]:
        latest_results = {}
        for r in reversed([r for r in self.monitoring_results if r.case_id == case_id]):
            if r.property_name not in latest_results:
                latest_results[r.property_name] = r

        return {
            "case_id": case_id,
            "overall_compliance": all(r.verdict for r in latest_results.values()),
            "properties": {
                prop: {
                    "verdict": r.verdict,
                    "timestamp": r.timestamp,
                    "violation_details": r.violation_details
                }
                for prop, r in latest_results.items()
            }
        }


class RFQMonitoringEngine:
    """Main monitoring engine with W_Nabellen->A_ACCEPTED checks"""

    def __init__(self):
        self.monitor = RFQMTLMonitor()
        self.processed_traces = []
        self.monitoring_results = []

    def load_and_process_traces(self, log_file: str):
        """Load and process traces with chain precedence checks"""
        print(f"Loading traces from: {log_file}")

        with open(log_file, 'r') as f:
            log_data = json.load(f)

        traces = log_data['traces']
        print(f"Loaded {len(traces)} traces")

        for trace in traces:
            results = self.monitor.process_trace(trace)
            self.monitoring_results.extend(results)
            self.processed_traces.append(trace)

        return self.monitoring_results

    def generate_monitoring_report(self) -> Dict[str, Any]:
        """Generate report showing which cases violated each pattern"""
        total_traces = len(self.processed_traces)

        # Initialize data structures
        property_violations = defaultdict(lambda: {'count': 0, 'cases': set()})
        case_violations = defaultdict(list)
        all_violating_cases = set()

        # Process all monitoring results
        for result in self.monitoring_results:
            if not result.verdict:
                # Track violations by property
                property_violations[result.property_name]['count'] += 1
                property_violations[result.property_name]['cases'].add(result.case_id)

                # Track violations by case
                case_violations[result.case_id].append({
                    'property': result.property_name,
                    'timestamp': result.timestamp,
                    'details': result.violation_details
                })
                all_violating_cases.add(result.case_id)

        # Calculate compliant cases
        compliant_cases = total_traces - len(all_violating_cases)

        # Build the report
        report = {
            "monitoring_summary": {
                "total_traces": total_traces,
                "compliant_traces": compliant_cases,
                "violating_traces": len(all_violating_cases),
                "compliance_rate": compliant_cases / total_traces if total_traces > 0 else 0,
            },
            "property_violations": {
                prop: {
                    'total_violations': data['count']
                    # 'violating_cases': list(data['cases'])
                } for prop, data in property_violations.items()
            },
            "case_violations": {
                case_id: violations
                for case_id, violations in case_violations.items()
            },
            "compliant_cases": [
                case_id for case_id in (case['case_id'] for case in self.processed_traces)
                if case_id not in all_violating_cases
            ]
        }

        # Print formatted output
        print("\nFinal Compliance Report:")
        print(f"Total traces: {total_traces}")
        print(f"Compliant cases: {compliant_cases}")
        print(f"Violating cases: {len(all_violating_cases)}")
        print(f"Compliance rate: {report['monitoring_summary']['compliance_rate']:.2%}")

        print("\n=== Property Violations ===")
        for prop, data in sorted(report['property_violations'].items()):
            if prop == "strict_chain_response":
                print(f"Strict Chain Response (A_ACCEPTED→w_completeren_aanvraag):")
                print(f"   Violations: {data['total_violations']}")
                # print(f"   Cases: {', '.join(data['violating_cases'])}")
            elif prop == "existence_o_declined":
                print(f"Missing O_DECLINED: {data['total_violations']} violations")
            else:
                print(f"{prop}: {data['total_violations']} violations")
                # print(f"   Cases: {', '.join(data['violating_cases'])}")

        print("\n=== Case Details ===")
        for case_id, violations in report['case_violations'].items():
            print(f"\nCase {case_id} violations:")
            for violation in violations:
                if violation['property'] == "strict_chain_response":
                    print(f" - Strict Chain Response at {violation['timestamp']}: {violation['details']}")
                else:
                    print(f" - {violation['property']} at {violation['timestamp']}: {violation['details']}")

        print("\nMonitoring completed!")
        return report

    def save_results(self, output_file: str):
        """Save monitoring results to JSON file"""
        report = self.generate_monitoring_report()

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Monitoring results saved to: {output_file}")
        return report


def main():
    """Main function with W_Nabellen->A_ACCEPTED monitoring"""
    print("=== RFQ Process Monitoring with W_Nabellen->A_ACCEPTED Chain Precedence ===\n")

    engine = RFQMonitoringEngine()

    # Process traces
    log_file = "/app/rfq_process_mining/traces/bpi2013_event_log.json"
    results = engine.load_and_process_traces(log_file)

    print(f"\n=== Monitoring Complete ===")
    print(f"Processed {len(results)} monitoring results")

    # Generate and save report
    output_file = "/app/rfq_process_mining/results/monitoring_report.json"
    report = engine.save_results(output_file)

    # Print summary
    summary = report['monitoring_summary']
    print(f"\n=== Summary ===")
    print(f"Total traces: {summary['total_traces']}")
    print(f"Compliant: {summary['compliant_traces']}")
    print(f"Violating: {summary['violating_traces']}")
    print(f"Compliance rate: {summary['compliance_rate']:.2%}")

    print("\n=== Property Violations ===")
    for prop, count in report['property_violations'].items():
        print(f"{prop}: {count} violations")


if __name__ == "__main__":
    main()