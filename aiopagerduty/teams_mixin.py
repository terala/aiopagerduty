"""Teams Mixin
"""

from aiopagerduty.fetcher import FetcherProtocol
from aiopagerduty.models import Team, TeamMember

from typing import List


class TeamsMixin:
    """Teams API Mixin
    """

    async def list_teams(self: FetcherProtocol) -> List[Team]:
        return await self.multi_fetch(Team, 'teams', 'teams')

    async def list_team_members(self: FetcherProtocol,
                                team: Team) -> List[TeamMember]:
        return await self.multi_fetch(TeamMember, f'teams/{team.id}/members',
                                      'members')
