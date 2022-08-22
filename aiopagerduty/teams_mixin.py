"""Teams Mixin
"""

from aiopagerduty.fetcher import FetcherProtocol
from aiopagerduty.models import Team, TeamMember


class TeamsMixin:
    """Teams API Mixin
    """
    async def list_teams(self: FetcherProtocol) -> list[Team]:
        return await self.multi_fetch(Team, 'teams', 'teams')

    async def list_team_members(self: FetcherProtocol, team: Team) -> list[TeamMember]:
        return await self.multi_fetch(TeamMember,
                                      f'teams/{team.id}/members', 'members')
