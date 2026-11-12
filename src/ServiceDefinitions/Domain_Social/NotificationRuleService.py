from uoishelpers.dataloaders.IDLoader import IDLoader

from src.DBDefinitions import NotificationRuleModel
from src.ServiceDefinitions.BaseService import BaseService
from src.ServiceDefinitions.ServiceContext import ServiceContext


class NotificationRuleService(BaseService[IDLoader[NotificationRuleModel]]):
    """Pravidla, podle kterých se uživateli generují notifikace."""

    @classmethod
    async def getLoader(cls, ctx: ServiceContext) -> IDLoader[NotificationRuleModel]:
        return ctx.loaders.NotificationRuleModel

    @classmethod
    async def GetEnabledRules(cls, ctx: ServiceContext, owner_id=None) -> list[NotificationRuleModel]:
        """Vrátí aktivní pravidla (volitelně jen pro daného vlastníka)."""
        loader = await cls.getLoader(ctx)
        filters = {'enabled': True}
        if owner_id is not None:
            filters['owner_id'] = owner_id
        return await loader.filter_by(**filters)

    @classmethod
    async def GetMatchingRules(cls, ctx: ServiceContext, entity_id, entity_type_id, activity_type_id) -> list[NotificationRuleModel]:
        """Najde aktivní pravidla odpovídající aktivitě.

        Pravidlo odpovídá, pokud každé z jeho vyplněných kritérií
        (entity_id, entity_type_id, activity_type_id) souhlasí; prázdné
        kritérium (None) znamená "libovolná hodnota".
        """
        rules = await cls.GetEnabledRules(ctx)

        def matches(rule_value, actual):
            return rule_value is None or rule_value == actual

        return [
            rule for rule in rules
            if matches(rule.entity_id, entity_id)
            and matches(rule.entity_type_id, entity_type_id)
            and matches(rule.activity_type_id, activity_type_id)
        ]