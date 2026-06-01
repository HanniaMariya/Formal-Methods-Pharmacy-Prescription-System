# Pharmacy System - Formal Methods Implementation

## Project Overview

This project implements a **Pharmacy Management System** with formal verification principles embedded into its design. The system manages prescriptions, patients, drugs, and dispensing operations while maintaining strict invariants and preconditions to ensure correctness and safety.

**Core Purpose**: Demonstrate application of formal methods principles (invariants, preconditions, state verification) in a real-world domain where patient safety and medication accuracy are critical.

---

## System Architecture

### Data Structures

The system consists of four main entities:

- **Patient**: Uniquely identified patient records with personal information
- **Drug**: Inventory management with stock tracking
- **Prescription**: Links a patient to a drug through a prescriber with quantity and status
- **DispenseEvent**: Audit trail of when and by whom prescriptions were dispensed

### Prescription Lifecycle

```
PENDING → DISPENSED (successful dispensing)
PENDING → CANCELLED (cancellation)
```

Only PENDING prescriptions can transition; terminal states are immutable.

---

## Formal Methods: Invariants

Invariants are conditions that **must always be true** after every operation. The system enforces two core invariants:

### Invariant I1: Referential Integrity
**Rule**: Every prescription must reference an existing patient AND an existing drug.

**Why**: This prevents orphaned records in the database. A prescription cannot reference a non-existent patient or drug, which would make the system state incoherent.

**Implementation**: `check_invariants()` validates this after each state-modifying operation.

```python
for prescription in self.prescriptions.values():
    if prescription.patient_id not in self.patients:
        raise ValueError("Invariant violated: patient does not exist")
    if prescription.drug_id not in self.drugs:
        raise ValueError("Invariant violated: drug does not exist")
```

### Invariant I2: Non-Negative Stock
**Rule**: Drug stock can never be negative (`stock ≥ 0`).

**Why**: Negative stock is physically impossible and indicates a critical error. This prevents overselling and maintains accurate inventory counts.

**Implementation**: Checked after every operation that modifies drug stock.

```python
for drug in self.drugs.values():
    if drug.stock < 0:
        raise ValueError("Invariant violated: stock cannot be negative")
```

**How it's Protected**: The `DispensePrescription` method explicitly checks if sufficient stock exists **before** reducing inventory:
```python
if drug.stock < prescription.quantity:
    raise ValueError("Insufficient stock")
```

---

## Formal Methods: Preconditions

Preconditions are **requirements that must be satisfied before an operation executes**. They prevent invalid state transitions.

### Operation: `IssuePrescription`

**Preconditions**:
1. Prescription ID must be unique (no duplicate prescriptions)
2. Patient must exist in system
3. Drug must exist in system
4. Prescriber must be licensed (registered in system)
5. **Separation of Roles**: Prescriber cannot issue prescription to themselves
6. Quantity must be positive (`quantity > 0`)

**Why Separation of Roles?** This is a **safety constraint** preventing conflict of interest. A prescriber self-prescribing could lead to inappropriate medication and abuse. In pharmacy systems, there must be separation between the person requesting medication (patient) and the person authorizing it (prescriber).

```python
if patient_id == prescriber_id:
    raise ValueError("A prescriber cannot issue a prescription to themselves")
```

### Operation: `DispensePrescription`

**Preconditions**:
1. Prescription must exist
2. Prescription status must be PENDING (not already dispensed or cancelled)
3. Sufficient stock must be available for the prescribed quantity

**Why Status Check?** Prevents double-dispensing. Once a prescription is dispensed, it's a completed transaction and cannot be repeated.

### Operation: `CancelPrescription`

**Preconditions**:
1. Prescription must exist
2. Status must be PENDING

**Why?** Only pending prescriptions can be cancelled because:
- Dispensed prescriptions represent completed medication fulfillment (cannot undo medication already given)
- Cancelled prescriptions are terminal (conceptually already "handled")

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Immutable Status Transitions** | Once a prescription moves to DISPENSED or CANCELLED, it cannot change. This creates an audit trail and prevents accidental reversals. |
| **Precondition Validation First** | All preconditions are checked before any state modification, ensuring atomicity—either the operation fully succeeds or fails cleanly. |
| **Invariant Checking After Every Operation** | Guarantees that the system never enters an invalid state, even if preconditions are bypassed or new code is added. |
| **Separation of Concerns** | Prescribers, pharmacists, and patients are distinct roles with specific permissions, preventing unauthorized medication access. |
| **Immutable Drug Stock Before Dispensing** | Stock is decremented only after all preconditions pass, preventing partial state updates on failure. |

---

## Usage Guide

### Basic Setup

```python
from pharmacy_system import PharmacySystem

system = PharmacySystem()

# Step 1: Register a prescriber (licensed)
system.add_prescriber("PR001")

# Step 2: Add a patient
system.AddPatient("P001", "Ali Khan", "2000-05-10")

# Step 3: Add a drug to inventory
system.AddDrug("D001", "Panadol", stock=100)

# Step 4: Issue a prescription
system.IssuePrescription(
    prescription_id="RX001",
    patient_id="P001",
    drug_id="D001",
    prescriber_id="PR001",
    quantity=10
)

# Step 5: Dispense the prescription
system.DispensePrescription(
    prescription_id="RX001",
    pharmacist_id="PH001",
    timestamp="2025-07-29 10:00"
)

# Step 6: Check results
print(system.QueryPrescriptionStatus("RX001"))  # PrescriptionStatus.DISPENSED
print(system.QueryDrugStock("D001"))             # 90 (100 - 10)
```

### Query Operations

```python
# Check prescription status
status = system.QueryPrescriptionStatus("RX001")

# Check current drug stock
stock = system.QueryDrugStock("D001")
```

---

## Error Handling & Constraints

The system is designed to **fail fast** with clear error messages. Examples of violations:

```python
# ❌ Duplicate patient
system.AddPatient("P001", "Name", "DOB")
system.AddPatient("P001", "Other", "DOB")  # ValueError: Patient already exists

# ❌ Non-existent patient
system.IssuePrescription("RX002", "UNKNOWN", "D001", "PR001", 5)  
# ValueError: Patient does not exist

# ❌ Insufficient stock
system.AddDrug("D002", "Aspirin", 5)
system.IssuePrescription("RX003", "P001", "D002", "PR001", 100)
system.DispensePrescription("RX003", "PH001", "2025-07-29")
# ValueError: Insufficient stock

# ❌ Separation of roles violated
system.add_prescriber("P001")  # Patient ID as prescriber
system.IssuePrescription("RX004", "P001", "D001", "P001", 5)
# ValueError: A prescriber cannot issue a prescription to themselves
```

---

## Verification Properties

This implementation ensures:

✅ **Safety**: Invariants I1 and I2 are always maintained  
✅ **Consistency**: Preconditions prevent invalid transitions  
✅ **Atomicity**: Operations either fully complete or fail without partial state changes  
✅ **Auditability**: Dispense log records all medication dispensing events  
✅ **Role Separation**: Patients and prescribers are distinct entities  

---

## Formal Methods Concepts Applied

| Concept | Application |
|---------|------------|
| **Invariants** | I1 (Referential Integrity), I2 (Non-negative Stock) |
| **Preconditions** | Validated before state modification in every operation |
| **State Space** | Discrete states (PENDING, DISPENSED, CANCELLED) with defined transitions |
| **Atomicity** | All-or-nothing operation semantics |
| **Audit Trail** | Dispense log for traceability |
| **Separation of Concerns** | Role-based constraints (prescriber ≠ patient) |

---

## Why This Matters

In pharmacy systems, formal methods are critical because:

1. **Patient Safety**: Incorrect medication or dosage can cause harm
2. **Legal Compliance**: Healthcare systems require provable correctness
3. **Financial Accuracy**: Drug inventory must match physical stock exactly
4. **Auditability**: Every transaction must be trackable and reversible (where applicable)
5. **No Silent Failures**: The system must never accept invalid operations

This implementation demonstrates how formal verification prevents real-world failures before they occur in production.

---

## Running the System

```bash
python pharmacy_system.py
```

The script includes comprehensive examples demonstrating:
- Valid operations and expected behavior
- Constraint violations and error handling
- Invariant maintenance through operations
- State queries

---

## Viva Discussion Points

- Why is the "prescriber cannot self-prescribe" rule necessary?
- How do invariants I1 and I2 guarantee system safety?
- Why check preconditions before state updates rather than after?
- What would happen without invariant checking?
- How does the system maintain an audit trail?
- Why are prescription status transitions immutable?
- How does this design scale to a real pharmacy system?

---

## Author Notes

This system demonstrates foundational formal methods principles in a domain-specific context. While simplified for educational purposes, the core concepts (invariants, preconditions, state verification) directly apply to real healthcare systems, financial software, and critical infrastructure.
