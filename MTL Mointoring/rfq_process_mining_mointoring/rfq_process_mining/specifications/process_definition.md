# Request for Quotation (RFQ) Process Mining with MTL Monitoring

## Process Definition

### Business Process: Request for Quotation (RFQ)

**Actors:**
- Company (Customer)
- Supplier (Vendor)

**Process Flow:**
1. Company sends RFQ to Supplier
2. Supplier prepares and sends Quotation to Company
3. Supplier preserves the offer for 1 week
4. Company may send Purchase Order (PO) within 3 weeks of quotation
5. Supplier accepts PO if within 3 weeks, otherwise denies

### Event Types

| Event | Description | Actor | Attributes |
|-------|-------------|-------|------------|
| `rfq_sent` | Company sends request for quotation | Company | case_id, timestamp, company_id, supplier_id |
| `quotation_prepared` | Supplier prepares quotation | Supplier | case_id, timestamp, quote_id, amount |
| `quotation_sent` | Supplier sends quotation to company | Supplier | case_id, timestamp, quote_date |
| `offer_preserved` | Supplier preserves offer (1 week) | Supplier | case_id, timestamp, expiry_date |
| `po_sent` | Company sends purchase order | Company | case_id, timestamp, po_id, quote_ref |
| `po_accepted` | Supplier accepts purchase order | Supplier | case_id, timestamp, acceptance_date |
| `po_denied` | Supplier denies purchase order | Supplier | case_id, timestamp, denial_reason |

### Timing Constraints

1. **Offer Preservation**: Supplier must preserve offer for exactly 1 week (7 days) after quotation
2. **PO Deadline**: Purchase order must be received within 3 weeks (21 days) from quotation date
3. **Response Rule**: If PO arrives after 3 weeks, supplier must deny it

## MTL Properties

### Property 1: Offer Preservation Compliance
```
MTL: G(quotation_sent -> F[0,7d] offer_preserved)
Reelay: quotation_sent implies eventually[0,604800] offer_preserved
Description: Every quotation must be followed by offer preservation within 7 days (604800 seconds)
```

### Property 2: Purchase Order Timing Compliance
```
MTL: G(po_sent -> (po_within_deadline or po_after_deadline))
Where:
- po_within_deadline = quotation_sent and F[0,21d] po_sent
- po_after_deadline = quotation_sent and F[21d,∞] po_sent

Reelay: po_sent implies (po_within_deadline or po_after_deadline)
Description: Every PO must be classified as either within or after deadline
```

### Property 3: Supplier Response Compliance
```
MTL: G((quotation_sent and F[0,21d] po_sent) -> F[0,1d] po_accepted)
Reelay: (quotation_sent and eventually[0,1814400] po_sent) implies eventually[0,86400] po_accepted
Description: If PO arrives within 21 days of quotation, supplier must accept within 1 day
```

### Property 4: Late PO Denial Compliance
```
MTL: G((quotation_sent and F[21d,∞] po_sent) -> F[0,1d] po_denied)
Reelay: (quotation_sent and eventually[1814400,∞] po_sent) implies eventually[0,86400] po_denied
Description: If PO arrives after 21 days of quotation, supplier must deny within 1 day
```

### Property 5: Mutual Exclusion of PO Response
```
MTL: G(po_sent -> ¬(po_accepted ∧ po_denied))
Reelay: po_sent implies not (po_accepted and po_denied)
Description: A PO cannot be both accepted and denied
```

## Time Units

- All timestamps in seconds since epoch
- 1 day = 86,400 seconds
- 1 week = 604,800 seconds  
- 3 weeks = 1,814,400 seconds

## Trace Structure

Each trace represents one RFQ case with the following structure:
```json
{
  "case_id": "RFQ_001",
  "events": [
    {
      "activity": "rfq_sent",
      "timestamp": 1640995200,
      "attributes": {
        "company_id": "COMP_A",
        "supplier_id": "SUPP_X"
      }
    },
    {
      "activity": "quotation_prepared", 
      "timestamp": 1641081600,
      "attributes": {
        "quote_id": "Q_001",
        "amount": 15000
      }
    }
  ]
}
```

## Compliance Scenarios

### Compliant Traces
1. **Perfect Compliance**: RFQ → Quotation → Offer Preserved → PO within 21 days → PO Accepted
2. **Late PO Properly Denied**: RFQ → Quotation → Offer Preserved → PO after 21 days → PO Denied
3. **No PO Sent**: RFQ → Quotation → Offer Preserved (no further action)

### Violating Traces
1. **Missing Offer Preservation**: RFQ → Quotation → PO → PO Accepted (no offer preservation)
2. **Late PO Incorrectly Accepted**: RFQ → Quotation → PO after 21 days → PO Accepted (should be denied)
3. **No Response to PO**: RFQ → Quotation → PO → (no acceptance/denial)
4. **Conflicting Responses**: RFQ → Quotation → PO → PO Accepted → PO Denied (both responses)

This process model captures realistic business constraints and timing requirements that can be monitored using MTL properties in Reelay.

