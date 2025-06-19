from dependency_injector import providers, containers
from dependency_injector.providers import Singleton

from services.analysis_service import AnalysisService
from services.brand_service import BrandService
from services.openai_service import OpenAIService


class ServicesContainer(containers.DeclarativeContainer):
    ai_service: Singleton = providers.Singleton(
        OpenAIService
    )
    analysis_service: Singleton = providers.Singleton(
        AnalysisService,
        ai_service=ai_service
    )

    brand_service: Singleton = providers.Singleton(
        BrandService,
        analysis_service=analysis_service
    )
