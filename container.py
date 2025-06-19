from dependency_injector import providers, containers
from dependency_injector.providers import Singleton

from services.analysis_service import AnalysisService
from services.openai_service import OpenAIService


class ServicesContainer(containers.DeclarativeContainer):
    ai_service: Singleton = providers.Singleton(
        OpenAIService
    )
    analysis_service: Singleton = providers.Singleton(
        AnalysisService,
        ai_service=ai_service
    )
