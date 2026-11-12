from uoishelpers.dataloaders.LoaderMapBase import LoaderMapBase
from uoishelpers.dataloaders.IDLoader import IDLoader

import src.DBDefinitions
from src.DBDefinitions import (
    BaseDBModel,
    EventModel,
    EventInvitationModel,
    NotificationModel,
    NotificationRuleModel,
    NotificationTypeModel,
)


class LoaderMap(LoaderMapBase[BaseDBModel]):
    BaseModel = BaseDBModel

    EventModel: IDLoader[src.DBDefinitions.EventModel] = None
    EventInvitationModel: IDLoader[src.DBDefinitions.EventInvitationModel] = None
    NotificationModel: IDLoader[src.DBDefinitions.NotificationModel] = None
    NotificationRuleModel: IDLoader[src.DBDefinitions.NotificationRuleModel] = None
    NotificationTypeModel: IDLoader[src.DBDefinitions.NotificationTypeModel] = None

    def __init__(self, session):
        super().__init__(session)
        self.EventModel = self.get(EventModel)
        self.EventInvitationModel = self.get(EventInvitationModel)
        self.NotificationModel = self.get(NotificationModel)
        self.NotificationRuleModel = self.get(NotificationRuleModel)
        self.NotificationTypeModel = self.get(NotificationTypeModel)

    def get_by_name(self, name: str):
        return getattr(self, name)


def createLoadersContext(session):
    """Compatibility helper for places expecting a dict context."""
    return {'loaders': LoaderMap(session)}