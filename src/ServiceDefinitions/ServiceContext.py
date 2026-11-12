import dataclasses
import typing

from src.Dataloaders import LoaderMap

if typing.TYPE_CHECKING:
    from src.ServiceDefinitions.Domain_Events.EventService import EventService as _EventService
    from src.ServiceDefinitions.Domain_Events.EventInvitationService import EventInvitationService as _EventInvitationService
    from src.ServiceDefinitions.Domain_Social.NotificationService import NotificationService as _NotificationService
    from src.ServiceDefinitions.Domain_Social.NotificationRuleService import NotificationRuleService as _NotificationRuleService
    from src.ServiceDefinitions.Domain_Social.NotificationTypeService import NotificationTypeService as _NotificationTypeService


@dataclasses.dataclass(frozen=True)
class ServiceRegistry:
    @property
    def EventService(self) -> type['_EventService']:
        from src.ServiceDefinitions.Domain_Events.EventService import EventService
        return EventService

    @property
    def EventInvitationService(self) -> type['_EventInvitationService']:
        from src.ServiceDefinitions.Domain_Events.EventInvitationService import EventInvitationService
        return EventInvitationService

    @property
    def NotificationService(self) -> type['_NotificationService']:
        from src.ServiceDefinitions.Domain_Social.NotificationService import NotificationService
        return NotificationService

    @property
    def NotificationRuleService(self) -> type['_NotificationRuleService']:
        from src.ServiceDefinitions.Domain_Social.NotificationRuleService import NotificationRuleService
        return NotificationRuleService

    @property
    def NotificationTypeService(self) -> type['_NotificationTypeService']:
        from src.ServiceDefinitions.Domain_Social.NotificationTypeService import NotificationTypeService
        return NotificationTypeService


SERVICES = ServiceRegistry()


@dataclasses.dataclass
class ServiceContext:
    loaders: LoaderMap
    user: typing.Any = None
    ug_client: typing.Callable[..., typing.Awaitable[typing.Any]] | None = None
    request: typing.Any = None
    session: typing.Any = None
    Services: ServiceRegistry = SERVICES

    # uoishelpers helpers commonly expect info.context to behave like a dict
    # with at least the key "loaders". Keeping these methods lets us pass a
    # typed ServiceContext directly as Strawberry context.
    def __getitem__(self, key: str) -> typing.Any:
        return getattr(self, key)

    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        return getattr(self, key, default)

    def __contains__(self, key: str) -> bool:
        return hasattr(self, key)