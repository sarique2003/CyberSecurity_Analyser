from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from container import ServicesContainer
from services.models import SecurityFramework, CSAMainCategory, NISTMainCategory, ISO27001MainCategory
analysis_router = APIRouter()

analysis_service = ServicesContainer.analysis_service()

@analysis_router.get("/content")
async def analyze_content():
    return await analysis_service.perform_profile_analysis(input_file_path='/data/wepay_security.pdf')


@analysis_router.get("/framework")
async def analyze_by_framework(
    framework: SecurityFramework = Query(..., description="Main security framework"),
    sub_category: Optional[str] = Query(None, description="Optional subcategory (main category)")
):
    # Validate sub_category against the selected framework's enum
    return await analysis_service.perform_framework_analysis(input_file_path='/data/wepay_security.pdf',
                                                             main_framework=framework, sub_category=sub_category)

