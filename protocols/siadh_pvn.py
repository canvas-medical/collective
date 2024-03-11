from canvas_workflow_kit.protocol import (
    ClinicalQualityMeasure,
    ProtocolResult,
    STATUS_DUE,
    STATUS_SATISFIED
)

from canvas_workflow_kit.constants import CHANGE_TYPE
from canvas_workflow_kit.recommendation import Recommendation, PrescribeRecommendation
from canvas_workflow_kit.value_set.value_set import ValueSet
from canvas_workflow_kit.timeframe import Timeframe

class TSSurgery(ValueSet):
    VALUE_SET_NAME = "Transsphenoidal Surgery"
    ICD10PCS = {
        '0BBH0ZZ',
        '0BBH3ZZ',
        '0BBH4ZZ',
        '0BBH8ZZ',
        '0BBJ0ZZ',
        '0BBJ3ZZ',
        '0BBJ4ZZ',
        '0BBJ8ZZ'
    }

    ICD9CM = {
        '07.61',
        '07.62',
        '07.63',
        '07.64',
        '07.65',
        '07.68',
        '07.69'
    }

    SNOMEDCT = {
        '46296006',
        '53158000',
        '67598004',
        '276274008',
        '446813000',
        '446814006',
        '726755001',
        '726756000'
    }

    CPT = {
        '62165',
        '61548'
    }

class FluidRestriction(ValueSet):
    VALUE_SET_NAME = "Fluid Restriction"
    ICD10PCS = {
        '4A0935Z',  # Measurement of Fluid Balance, Monitoring, External Approach
        '4A0945Z',  # Measurement of Fluid Balance, Monitoring, Internal Approach
        '4A0955Z',  # Measurement of Fluid Balance, Monitoring, Circulatory Approach
        '4A0965Z'  # Measurement of Fluid Balance, Monitoring, Respiratory Approach
    }

    ICD9CM = {
        '25.82'  # Fluid restriction
    }

    SNOMEDCT = {
        '61426000',  # Fluid intake restriction
        '226355009',  # Restriction of fluid intake
        '226358006',  # Fluid balance management
        '243807004',  # Strict fluid balance management
        '274411005',  # Fluid restriction education
        '286024002',  # Monitoring of fluid input/output
        '361231003',  # Fluid restriction therapy
        '443288003',  # Fluid balance education
        '710742001',  # Monitoring of fluid restriction
        '710743006'  # Fluid restriction regimen
    }

class MyFirstProtocol(ClinicalQualityMeasure):

    class Meta:

        title = 'Ed Laws SIADH Prevention Protocol'

        description = 'The protocol Ed Laws and I published to prevent SIADH in post-op TSS patients'

        version = ''

        information = ''

        identifiers = ['CMS12345v1']

        types = ['CQM']

        compute_on_change_types = [
            CHANGE_TYPE.CONDITION
        ]

        references = [
            'Protocol Reference https://pubmed.ncbi.nlm.nih.gov/29075986/'
        ]


    def in_denominator(self):
        """
        Patients who have had the surgery.
        """
        return self.patient.procedures.find(TSSurgery)

    def in_numerator(self):
        """
        Patients who have had the surgery in the window of intervention.
        """
        last_TS_surgery_timeframe = Timeframe(self.now.shift(days=-7), self.now)
        TSSurg_screening = self.patient.interviews.find(
            TSSurgery
        ).within(last_TS_surgery_timeframe)
        return bool(TSSurg_screening)

    def compute_results(self):
        result = ProtocolResult()

        if self.in_denominator():  # if they have had TSS
            if self.in_numerator():  # If they had TSS in last 7 days (otherwise they are outside the window)
                result.status = STATUS_DUE
                result.due_in = -1
                result.add_narrative(
                    f'{self.patient.first_name} should be prescribed fluid restriction'
                )

                result.add_recommendation(
                    PrescribeRecommendation(
                        key='PRESCRIBE_WATER_RESTRICTION',
                        rank=1,
                        button="Prescribe",
                        patient=self.patient,
                        prescription=FluidRestriction,
                        title='Interview Patient About Choices',
                        context={
                            'sig_original_input': 'restrict fluid intake to 1 liter per day for 7 days',
                            'duration_in_days': 7,
                            'dispense_quantity': 1
                        }
                    )
                )
        return result
