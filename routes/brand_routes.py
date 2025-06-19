from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from container import ServicesContainer
from services.models import SecurityFramework, CSAMainCategory, NISTMainCategory, ISO27001MainCategory
brand_router = APIRouter()
brand_service = ServicesContainer.brand_service()


@brand_router.get("/quantify")
async def quantify_brand_risk(brand_id: int = Query(..., description="Brand ID"),
                              framework: SecurityFramework = Query(..., description="Main security framework")):
    return await brand_service.quantify_brand_risk(brand_id=brand_id, framework=framework)
