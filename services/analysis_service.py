import fitz
import json
import pandas as pd
from pydantic import TypeAdapter
from services.openai_service import OpenAIService
from pathlib import Path
from typing import Optional
from jinja2 import Environment, FileSystemLoader
from services.models import ComplianceStatus, ComplianceDetails, SystemCompliance, FrameworkAnalysis, FrameworkReport, \
    SecurityFramework, get_main_category_enum

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "prompts"


class AnalysisService:
    def __init__(self, ai_service: OpenAIService):
        self.ai_service = ai_service

    def _render_template(self, template_path: str, **context) -> str:
        """Render the Jinja template with the given context."""
        try:
            # Load the Jinja environment and template
            env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
            template = env.get_template(template_path)
            # Render the template with the provided context
            return template.render(context)
        except Exception as e:
            return f"Error rendering template: {str(e)}"

    def calculate_framework_compliance_score(self, assessments: list[FrameworkAnalysis]) -> float:
        """
        Calculate the compliance score as: YES / (YES + NO)
        Returns a percentage score between 0 and 100.
        """
        total = len(assessments)
        if total == 0:
            return 0.0

        compliant_count = sum(1 for a in assessments if a.compliant.strip().lower() == "yes")
        score = (compliant_count / total) * 100
        return round(score, 2)

    async def read_document(self, input_file_path: str) -> str:
        extracted_text = ""
        with fitz.open(input_file_path) as pdf_document:
            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)
                page_text = page.get_text("text")
                extracted_text += page_text

        return extracted_text

    async def assign_main_category_score(self, analysed_system_compliance: SystemCompliance):
        compliant_count = sum(
            1 for section in
            [analysed_system_compliance.CSA, analysed_system_compliance.NIST, analysed_system_compliance.ISO_27001]
            if section.compliance_status == ComplianceStatus.COMPLIANT
        )

        # Assign score based on the compliant_count
        if compliant_count == 3:
            analysed_system_compliance.compliance_score = 3
        elif compliant_count == 2:
            analysed_system_compliance.compliance_score = 2
        else:
            analysed_system_compliance.compliance_score = 1

        return analysed_system_compliance

    async def perform_profile_analysis(self, input_file_path: str) -> Optional[SystemCompliance| dict]:
        extracted_text = ""
        try:
            extracted_text: str = await self.read_document(input_file_path)
            input_system_description = extracted_text
            if not input_system_description:
                input_system_description = "No system description found in the document."

            analysis_prompt: str = self._render_template("core_analysis.jinja", input_system_description=input_system_description)
            ai_response: str = await self.ai_service.make_llm_call(prompt=analysis_prompt)
            ai_response_text: str = ai_response.strip("```json").strip("```")
            json_response: dict = json.loads(ai_response_text, strict=False)
            system_compliance_response: SystemCompliance = SystemCompliance(**json_response)
            return await self.assign_main_category_score(system_compliance_response)

        except Exception as e:
            return {"error": f"Error reading PDF or template: {str(e)}"}

    async def extract_framework_details(self, main_framework: str, sub_category: Optional[str] = None) -> pd.DataFrame:
        df_combined = pd.read_csv('/Users/mohdsarique/Documents/Cyber_risk/pythonProject/data/frameworks.csv')
        normalized_framework = main_framework.value.strip().upper()
        filtered_df = df_combined[
            df_combined["Framework"].astype(str).str.strip().str.upper() == normalized_framework
            ]

        if sub_category:
            filtered_df = filtered_df[
                filtered_df["Main Category"].astype(str).str.strip().str.upper() == sub_category.strip().upper()
                ]
        result_df = filtered_df[["Control Number", "Control Title", "Purpose", "Main Category", "Framework"]].reset_index(drop=True)
        return result_df

    async def perform_framework_analysis(self, input_file_path: str, main_framework: str, sub_category: Optional[str] = None):
        try:
            extracted_text: str = await self.read_document(input_file_path)
            input_system_description = extracted_text
            framework_details: pd.DataFrame = await self.extract_framework_details(main_framework, sub_category)
            framework_analysis_prompt: str = self._render_template("framework_analysis.jinja",
                                                                   framework_name=main_framework,
                                                                   input_system_description=input_system_description, framework_details=framework_details)
            ai_response: str = await self.ai_service.make_llm_call(prompt=framework_analysis_prompt)
            ai_response_text: str = ai_response.strip("```json").strip("```")
            json_response: dict = json.loads(ai_response_text, strict=False)
            adapter = TypeAdapter(list[FrameworkAnalysis])
            assessments: list[FrameworkAnalysis] = adapter.validate_python(json_response)
            compliance_score: float = self.calculate_framework_compliance_score(assessments)

            framework_enum: SecurityFramework = SecurityFramework(main_framework)
            sub_category_enum = get_main_category_enum(framework_enum, sub_category) if sub_category else None
            framework_report = FrameworkReport(
                framework=framework_enum,
                framework_analysis=assessments,
                main_category=sub_category_enum,
                compliance_score=compliance_score
            )
            return framework_report.model_dump(by_alias=True)
        except Exception as e:
            print(e)
