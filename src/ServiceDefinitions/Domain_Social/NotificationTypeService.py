from uoishelpers.dataloaders.IDLoader import IDLoader

from src.DBDefinitions import NotificationTypeModel
from src.ServiceDefinitions.BaseService import BaseService
from src.ServiceDefinitions.ServiceContext import ServiceContext


class NotificationTypeService(BaseService[IDLoader[NotificationTypeModel]]):
    """Číselník typů entit a typů aktivit (stromová struktura)."""

    @classmethod
    async def getLoader(cls, ctx: ServiceContext) -> IDLoader[NotificationTypeModel]:
        return ctx.loaders.NotificationTypeModel