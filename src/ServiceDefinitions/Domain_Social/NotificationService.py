import uuid

from uoishelpers.dataloaders.IDLoader import IDLoader

from src.DBDefinitions import NotificationModel
from src.ServiceDefinitions.BaseService import BaseService, ServiceExceptionWithCode
from src.ServiceDefinitions.ServiceContext import ServiceContext


def _current_user_id(ctx: ServiceContext):
    user = ctx.user
    user_id = user.get('id') if isinstance(user, dict) else getattr(user, 'id', None)
    return uuid.UUID(user_id) if isinstance(user_id, str) else user_id


class NotificationService(BaseService[IDLoader[NotificationModel]]):
    """Notifikace určené konkrétnímu uživateli."""

    @classmethod
    async def getLoader(cls, ctx: ServiceContext) -> IDLoader[NotificationModel]:
        return ctx.loaders.NotificationModel

    @classmethod
    async def GetUnread(cls, ctx: ServiceContext, owner_id=None) -> list[NotificationModel]:
        """Nepřečtené notifikace vlastníka (výchozí je aktuální uživatel)."""
        loader = await cls.getLoader(ctx)
        owner_id = owner_id or _current_user_id(ctx)
        return await loader.filter_by(owner_id=owner_id, read=False)

    @classmethod
    async def MarkAsRead(cls, ctx: ServiceContext, entity) -> NotificationModel:
        """Označí notifikaci jako přečtenou; smí to jen její vlastník.

        `entity` musí obsahovat `id` a `lastchange` (optimistic concurrency).
        """
        loader = await cls.getLoader(ctx)
        notification = await loader.load(entity.id)
        if notification is None:
            raise ServiceExceptionWithCode('Notification not found', code='notification_not_found', location='MarkAsRead')

        if _current_user_id(ctx) != notification.owner_id:
            raise ServiceExceptionWithCode('You are not the owner of the notification', code='notification_not_owner', location='MarkAsRead')

        entity.read = True
        return await loader.update(entity=entity)