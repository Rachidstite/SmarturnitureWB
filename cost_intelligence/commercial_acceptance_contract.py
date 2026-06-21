from dataclasses import dataclass


@dataclass
class CommercialAcceptanceContract:
    acceptance_status: str = "DRAFT"
    quote_reference: str = ""
    customer_reference: str = ""
    quote_revision_reference: str = ""
    accepted_at: str = ""
    approved_at: str = ""
    confirmed_at: str = ""
    accepted_by: str = ""
    approved_by: str = ""
    confirmed_by: str = ""

    @property
    def quote_accepted(self):
        return self.acceptance_status in (
            "ACCEPTED",
            "APPROVED",
            "CONFIRMED",
        )

    @property
    def customer_approved(self):
        return self.acceptance_status in (
            "APPROVED",
            "CONFIRMED",
        )

    @property
    def confirmed_order(self):
        return self.acceptance_status == "CONFIRMED"
