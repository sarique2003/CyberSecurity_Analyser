from typing import Optional
import pandas as pd

from services.analysis_service import AnalysisService
from services.models import FrameworkReport, CyberRiskEstimate


class BrandService:
    def __init__(self, analysis_service: AnalysisService):
        self.analysis_service = analysis_service

    async def get_brand_metadata_by_id(self, brand_id: int) -> Optional[dict]:
        try:
            df = pd.read_csv("/Users/mohdsarique/Documents/Cyber_risk/pythonProject/data/brands.csv")
            filtered_df: pd.DataFrame = df[df["id"] == brand_id]

            if filtered_df.empty:
                return None

            row = filtered_df.iloc[0]
            return {
                "brand_id": int(row["id"]),
                "brand_name": str(row["brand_name"]),
                "total_asset_value": float(row["total_asset_value"]),
                "aro": float(row["aro"]),
                "document": str(row["document"])
            }

        except Exception as e:
            print(f"Error reading brand metadata: {e}")
            return None

    def quantify_cyber_risk(self, compliance_score: float, asset_value: float, aro: float) -> CyberRiskEstimate:
        """
        Estimate cyber risk in monetary terms based on compliance score, asset value, and ARO.

        Returns a dictionary with:
        - residual risk percent
        - monetary risk exposure
        - annualized loss expectancy (ALE)
        """
        try:
            risk_gap = (100 - compliance_score) / 100
            monetary_risk_exposure = round(risk_gap * asset_value, 2)
            ale = round(monetary_risk_exposure * aro, 2)

            return CyberRiskEstimate(
                residual_risk_percent=round(risk_gap * 100, 2),
                monetary_risk_exposure=monetary_risk_exposure,
                estimated_annualized_loss=ale
            )
        except Exception as e:
            print(f'Failed to calculate cyber risk: {str(e)}')

    async def quantify_brand_risk(self, brand_id: int, framework: str) -> CyberRiskEstimate:
        try:
            brand_information = await self.get_brand_metadata_by_id(brand_id=brand_id)
            input_file = brand_information.get('document')
            input_file_path = f"/Users/mohdsarique/Documents/Cyber_risk/pythonProject/data/{input_file}"
            framework_analysed_report: FrameworkReport = await self.analysis_service.perform_framework_analysis(input_file_path=input_file_path,
                                                                                               main_framework=framework)
            quantified_risk_output: CyberRiskEstimate = self.quantify_cyber_risk(
                compliance_score=framework_analysed_report["Compliance Score"],
                asset_value=brand_information["total_asset_value"],
                aro=brand_information["aro"]
            )
            return quantified_risk_output
        except Exception as e:
            print(f"Error reading brand metadata: {e}")
            return None