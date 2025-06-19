from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Union, Optional
from enum import Enum


class ComplianceStatus(str, Enum):
    COMPLIANT = "Compliant"
    NON_COMPLIANT = "Non Compliant"


class ComplianceDetails(BaseModel):
    compliance_status: ComplianceStatus
    positives: List[str]
    negatives: List[str]


class SystemCompliance(BaseModel):
    CSA: ComplianceDetails
    NIST: ComplianceDetails
    ISO_27001: ComplianceDetails
    compliance_score: Optional[int] = None


class SecurityFramework(Enum):
    CSA = "CSA"
    ISO27001 = "ISO27001"
    NIST = "NIST"


class CSAMainCategory(Enum):
    A = "A"
    B = "B"
    C = "C"


class NISTMainCategory(Enum):
    AC = "AC"
    AU = "AU"
    DE_CM = "DE.CM"
    DE_DP = "DE.DP"
    ID_AM = "ID.AM"
    ID_BE = "ID.BE"
    PR_AC = "PR.AC"
    PR_DS = "PR.DS"
    RC_IM = "RC.IM"
    RC_RP = "RC.RP"
    RS_CO = "RS.CO"
    RS_RP = "RS.RP"


class ISO27001MainCategory(Enum):
    _5 = "5"
    _6 = "6"
    _7 = "7"
    _8 = "8"


def get_main_category_enum(framework: SecurityFramework, value: str):
    try:
        if framework == SecurityFramework.CSA:
            return CSAMainCategory(value)
        elif framework == SecurityFramework.NIST:
            return NISTMainCategory(value)
        elif framework == SecurityFramework.ISO27001:
            return ISO27001MainCategory("_" + value if value.isdigit() else value)
    except ValueError:
        return None


class FrameworkAnalysis(BaseModel):
    control_number: str = Field(..., alias="Control Number")
    control_title: str = Field(..., alias="Control Title")
    purpose: str = Field(..., alias="Purpose")
    analysis: str = Field(..., alias="Analysis")
    compliant: Literal["Yes", "No"] = Field(..., alias="Complaint")


class FrameworkReport(BaseModel):
    framework: SecurityFramework
    compliance_score: Optional[float] = Field(default=None, alias="Compliance Score")
    main_category: Optional[Union[CSAMainCategory, ISO27001MainCategory, NISTMainCategory]] = None
    framework_analysis: list[FrameworkAnalysis] = []

    model_config = {
        "populate_by_name": True,  # ✅ allows setting `compliance_score` even though alias is defined
        "json_encoders": {
            float: lambda x: round(x, 2),
        }
    }


class CyberRiskEstimate(BaseModel):
    residual_risk_percent: float = Field(..., description="Remaining risk after compliance, as a percentage")
    monetary_risk_exposure: float = Field(..., description="Total dollar value of risk exposure")
    estimated_annualized_loss: float = Field(..., description="Estimated annualized loss expectancy (ALE)")

# Example usage
compliance_data = {
    "CSA": {
        "compliance_status": "Compliant",
        "positives": [
            "Adherence to industry-recognized cybersecurity frameworks including ISO 27001",
            "Regular security audits and compliance with data protection regulations"
        ],
        "negatives": []
    },
    "NIST": {
        "compliance_status": "Compliant",
        "positives": [
            "Implementation of the NIST Cybersecurity Framework tailored to fintech needs",
            "Comprehensive risk assessments and incident response plans"
        ],
        "negatives": []
    },
    "ISO_27001": {
        "compliance_status": "Compliant",
        "positives": [
            "Maintenance of an Information Security Management System (ISMS)",
            "Regular security audits and detailed security policies and procedures"
        ],
        "negatives": []
    }
}

if __name__ == "__main__":
    compliance = SystemCompliance(**compliance_data)
    print(compliance.model_dump_json(indent=2))

