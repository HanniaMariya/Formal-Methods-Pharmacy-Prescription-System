from dataclasses import dataclass
from enum import Enum

class PrescriptionStatus(Enum):
    PENDING = "pending"
    DISPENSED = "dispensed"
    CANCELLED = "cancelled"

@dataclass
class Patient:
    patient_id: str
    name: str
    date_of_birth: str

@dataclass
class Drug:
    drug_id: str
    name: str
    stock: int

@dataclass
class Prescription:
    prescription_id: str
    patient_id: str
    drug_id: str
    prescriber_id: str
    quantity: int
    status: PrescriptionStatus

@dataclass
class DispenseEvent:
    prescription_id: str
    pharmacist_id: str
    timestamp: str

class PharmacySystem:
    def __init__(self):
        self.patients = {}
        self.drugs = {}
        self.prescriptions = {}
        self.prescribers = set()
        self.dispense_log = []
    
    def check_invariants(self):

        # I1: every prescription references existing patient and drug
        for prescription in self.prescriptions.values():
            if prescription.patient_id not in self.patients:
                raise ValueError(
                    "Invariant violated: patient does not exist"
                )
            if prescription.drug_id not in self.drugs:
                raise ValueError(
                    "Invariant violated: drug does not exist"
                )
            
        # I2: stock >= 0
        for drug in self.drugs.values():
            if drug.stock < 0:
                raise ValueError(
                    "Invariant violated: stock cannot be negative"
                )  

    def add_prescriber(self, prescriber_id):
        self.prescribers.add(prescriber_id) # simple to populate prescribers, no invariants to check

    def AddPatient(self, patient_id: str, name: str, date_of_birth: str):
        # Precondition: patient_id is unique
        if patient_id in self.patients:
            raise ValueError("Patient already exists")
        
        # State update
        self.patients[patient_id] = Patient(
            patient_id, 
            name, 
            date_of_birth
        )
        # Check invariants
        self.check_invariants()     
    
    def AddDrug(self, drug_id: str, name: str, stock: int):
        # Precondition: drug_id is unique, stock >= 0
        if drug_id in self.drugs:
            raise ValueError("Drug already exists")
        if stock < 0:
            raise ValueError("Stock cannot be negative")
        
        # State update
        self.drugs[drug_id] = Drug(
            drug_id, 
            name, 
            stock
        )
        # Check invariants
        self.check_invariants()


    def IssuePrescription(
        self,
        prescription_id: str,
        patient_id: str,
        drug_id: str,
        prescriber_id: str,
        quantity: int
    ):
        # Preconditions
        if prescription_id in self.prescriptions:
            raise ValueError("Prescription already exists")

        if patient_id not in self.patients:
            raise ValueError("Patient does not exist")

        if drug_id not in self.drugs:
            raise ValueError("Drug does not exist")

        if prescriber_id not in self.prescribers:
            raise ValueError("Prescriber is not licensed")

        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

        # State update
        self.prescriptions[prescription_id] = Prescription(
            prescription_id,
            patient_id,
            drug_id,
            prescriber_id,
            quantity,
            PrescriptionStatus.PENDING
        )

        self.check_invariants()

    def DispensePrescription(
        self,
        prescription_id: str,
        pharmacist_id: str,
        timestamp: str
    ):
        # Preconditions
        if prescription_id not in self.prescriptions:
            raise ValueError("Prescription does not exist")

        prescription = self.prescriptions[prescription_id]

        if prescription.status != PrescriptionStatus.PENDING:
            raise ValueError(
                "Prescription is not pending"
            )

        drug = self.drugs[prescription.drug_id]

        if drug.stock < prescription.quantity:
            raise ValueError(
                "Insufficient stock"
            )

        # State updates
        prescription.status = PrescriptionStatus.DISPENSED
        drug.stock -= prescription.quantity
        self.dispense_log.append(
            DispenseEvent(
                prescription_id,
                pharmacist_id,
                timestamp
            )
        )

        self.check_invariants()

    def CancelPrescription(
        self,
        prescription_id: str
    ):
        # Preconditions
        if prescription_id not in self.prescriptions:
            raise ValueError(
                "Prescription does not exist"
            )
        prescription = self.prescriptions[prescription_id]

        if prescription.status != PrescriptionStatus.PENDING:
            raise ValueError(
                "Only pending prescriptions can be cancelled"
            )

        # State update
        prescription.status = PrescriptionStatus.CANCELLED

        self.check_invariants()

    def QueryPrescriptionStatus(
        self,
        prescription_id: str
    ):
        if prescription_id not in self.prescriptions:
            raise ValueError(
                "Prescription does not exist"
            )
        return self.prescriptions[
            prescription_id
        ].status

    def QueryDrugStock(
        self,
        drug_id: str
    ):
        if drug_id not in self.drugs:
            raise ValueError(
                "Drug does not exist"
            )
        return self.drugs[drug_id].stock
    

if __name__ == "__main__":

    system = PharmacySystem()

    print("=== Adding Prescriber ===")
    system.add_prescriber("PR001")
    print("Prescribers:", system.prescribers)

    print("\n=== Adding Patient ===")
    system.AddPatient(
        "P001",
        "Ali Khan",
        "2000-05-10"
    )
    print(system.patients)

    print("\n=== Adding Drug ===")
    system.AddDrug(
        "D001",
        "Panadol",
        100
    )
    print(system.drugs)

    print("\n=== Current System State ===")

    print("Patients:")
    for patient in system.patients.values():
        print(patient)

    print("\nDrugs:")
    for drug in system.drugs.values():
        print(drug)

    print("\nPrescribers:")
    print(system.prescribers)

    print("\nAll invariants satisfied.")

    print("\n=== Issue Prescription ===")

    system.IssuePrescription(
        "RX001",
        "P001",
        "D001",
        "PR001",
        10
    )

    print(system.prescriptions)

    print("\n=== Query Status ===")

    print(
        system.QueryPrescriptionStatus(
            "RX001"
        )
    )

    print("\n=== Dispense Prescription ===")

    system.DispensePrescription(
        "RX001",
        "PH001",
        "2025-07-29 10:00"
    )

    print(
        system.QueryPrescriptionStatus(
            "RX001"
        )
    )

    print(
        "Remaining stock:",
        system.QueryDrugStock("D001")
    )

    print("\n=== Dispense Log ===")
    print(system.dispense_log)

    try:
        system.AddPatient(
            "P001",
            "Another Person",
            "2001-01-01"
        )
    except ValueError as e:
        print(e)    

    try:
        system.IssuePrescription(
            "RX999",
            "UNKNOWN",
            "D001",
            "PR001",
            5
        )
    except ValueError as e:
        print(e)

    try:
        system.IssuePrescription(
            "RX002",
            "P001",
            "D001",
            "PR001",
            500
        )

        system.DispensePrescription(
            "RX002",
            "PH001",
            "2025-07-29"
        )

    except ValueError as e:
        print(e)