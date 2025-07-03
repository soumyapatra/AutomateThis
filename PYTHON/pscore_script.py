import logging
from core.restframework import ExpectationFailedException
from core.utils import transaction
from external.choices import ExternalCallBackEventType
from external.utils.manual_verification import ManualVerfication
from products.choices import LoanApplicationStatus
from products.models import LoanApplication
from products.services import ProductPolicyProxy
from sbt.services import LoanApplicationService
from users.utils.entity import process_platform_entities
from rest_framework.exceptions import ValidationError, APIException

LOGGER = logging.getLogger(__name__)


def raise_error_on_application_status_change(application):
    # handling application changes due to reassessment
    if application.status == LoanApplicationStatus.Rejected:
        raise ExpectationFailedException(
            "sorry, your application was rejected", code="application_rejected"
        )
    elif application.status == LoanApplicationStatus.Cancelled:
        raise ExpectationFailedException(
            "sorry, your application was cancelled", code="application_cancelled"
        )
    elif application.status == LoanApplicationStatus.PlanSelected:
        raise ExpectationFailedException(
            "sorry, your application was reopened", code="application_reopened"
        )


def main(pk):
    application = LoanApplication.objects.get(pk=pk)
    product_policy = ProductPolicyProxy.for_application(application)
    # handling application changes due to reassessment
    raise_error_on_application_status_change(application)

    all_entities_preapproved = None
    if product_policy.is_hybrid_preapproval_and_approval_enabled():
        """
        This section is currently applicable for Xpress only.
        As Xpress can support auto/manual preapproval or approval of the application.
        Other product policies won't implement this section
        """
        all_entities_preapproved = process_platform_entities(application)
        ManualVerfication().check_eligibility_and_update_reasons(application=application)

    if not product_policy.is_eligible_for_auto_pre_approval(application):
        raise ValidationError(f"auto approval not applicable for application id: {pk}")

    if all_entities_preapproved and product_policy.is_eligible_for_auto_pre_approval(
            application=application
    ):
        loan_application_service = LoanApplicationService(loan_application=application, auth_user=None)
        loan_application_service.auto_preapprove(
            should_trigger_external_callback=application.master_user.should_trigger_callback_to_source(
                ExternalCallBackEventType.ApplicationPreApproved
            )
        )

        # handling application changes due to reassessment
        raise_error_on_application_status_change(application.refresh())


loan_application_ids = [2100701, 29281114]
success = []
fail = []

for i in loan_application_ids:
    with transaction.atomic():
        try:
            main(pk=i)
            success.append(i)
        except Exception as ex:
            LOGGER.error(f"Loanapplication id : {i} , error : {ex}")
            fail.append(i)

print("Success app id : ", success)
print("Fail app id : ", fail)
