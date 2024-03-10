from canvas_workflow_kit.protocol import (
    ClinicalQualityMeasure,
    ProtocolResult,
    STATUS_DUE,
    STATUS_SATISFIED,
)

from canvas_workflow_kit.constants import CHANGE_TYPE
from canvas_workflow_kit.recommendation import InterviewRecommendation
from canvas_workflow_kit.value_set import ValueSet


class OSAHS(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a diagnosis of OSAHS.

    **Data Element Scope:** This value set may use a model element related to Diagnosis.

    **Inclusion Criteria:** Includes concepts that represent a diagnosis of OSAHS.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** ---
    """

    VALUE_SET_NAME = "OSAHS"
    OID = ""
    DEFINITION_VERSION = ""
    EXPANSION_VERSION = ""

    ICD10CM = {
        "G4733",  # Obstructive sleep apnea (adult) (pediatric)
    }
    SNOMEDCT = {
        "101301000119106",  # Obstructive sleep apnea (adult) (pediatric)
    }


class SleepClinicAssessment(ValueSet):
    VALUE_SET_NAME = "Sleep clinic with consultant"
    LOINC = {"70002-1"}


class SleepApnoeaOfferCPAP(ClinicalQualityMeasure):
    class Meta:

        title = (
            "Obstructive Sleep Apnoea Hypopnoea Syndrome CPAP Recommendation"
        )

        description = (
            "Assesses if a patient should be offered CPAP for obstructive "
            "sleep apnoea hypopnoea syndrome"
        )

        version = "0.001"

        information = "https://docs.canvasmedical.com"

        identifiers = ["G4733"]

        types = []

        compute_on_change_types = [
            CHANGE_TYPE.CONDITION,
            CHANGE_TYPE.LAB_REPORT,
        ]

        references = [
            "Protocol Reference https://www.nice.org.uk/guidance/ng202/resources/visual-summary-on-osahs-investigations-and-treatment-pdf-9204628717"
        ]

    def in_denominator(self) -> bool:
        """
        Patients in the initial population.
        """
        # Check if the patient has a diagnosis of OSAHS
        if self.patient.conditions.find(OSAHS):
            return True

        return False

    def in_numerator(self) -> bool:
        """
        Patients that have already been notified.
        """
        # check if patient already offered CPAP
        return False

    def compute_results(self) -> ProtocolResult:
        result = ProtocolResult()

        if self.in_denominator():
            if self.in_numerator():
                result.status = STATUS_SATISFIED
                result.add_narrative(
                    f"{self.patient.first_name} has already been offered CPAP"
                )
            else:
                result.status = STATUS_DUE
                result.due_in = -1
                result.add_narrative(
                    f"{self.patient.first_name} should be offered CPAP treatment"
                )

                result.add_recommendation(
                    InterviewRecommendation(
                        key="CPAP_offer",
                        rank=1,
                        button="Interview",
                        patient=self.patient,
                        questionnaires=[SleepClinicAssessment],
                        title="Offer CPAP",
                    )
                )
        return result
