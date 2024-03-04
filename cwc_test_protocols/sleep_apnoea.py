from canvas_workflow_kit.protocol import (
    ClinicalQualityMeasure,
    ProtocolResult,
    STATUS_DUE,
    STATUS_SATISFIED,
)


from canvas_workflow_kit.constants import CHANGE_TYPE
from canvas_workflow_kit.recommendation import InterviewRecommendation


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

        identifiers = []

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
        if self.patient.has_condition("OSAHS"):
            # Check if the patient has a recent sleep study
            if self.patient.has_lab_report("Sleep Study"):
                # check if moderate or severe OSAHS
                if self.patient.get_lab_report("Sleep Study").result in [
                    "Moderate",
                    "Severe",
                ]:
                    return True
                else:
                    return False

    def in_numerator(self) -> bool:
        """
        Patients that have already been notified.
        """
        # check if patient already offered CPAP
        if not self.patient.has_medication("CPAP"):
            return True
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
                        title=f"Offer CPAP",
                    )
                )
        return result
