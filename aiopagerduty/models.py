"""Data Models for PagerDuty API
"""

import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, EmailStr


class ObjectRef(BaseModel):
    id: str
    summary: str
    self: str    # url
    html_url: str | None  # Vendor does not always have a html_url defined
    type: str


class SupportHours(BaseModel):
    type: str
    time_zone: str
    days_of_week: list[int]
    start_time: str
    end_time: str


class ServiceStatus(str, Enum):
    ACTIVE = 'active'
    WARNING = 'warning'
    CRITICAL = 'critical'
    MAINTENANCE = 'maintenance'
    DISABLED = 'disabled'


class Team(ObjectRef):
    name: str
    description: str | None


# class IncidentUrgencyType(str, Enum):
#     constant = 'constant'
#     support_hours = 'use_support_hours'

# class IncidentUrgency(str, Enum):
#     low = 'low'
#     high = 'high'
#     severity_based = 'severity_based'


class IncidentUrgencyDefinition(BaseModel):
    urgency: Literal['low', 'high', 'severity_based']
    type: Literal['constant', 'user_support_hours']


class IncidentUrgencyRule(IncidentUrgencyDefinition):
    during_support_hours: IncidentUrgencyDefinition | None
    outside_support_hours: IncidentUrgencyDefinition | None


class Service(ObjectRef):
    """Service defined in PagerDuty
    """
    name: str
    description: str | None
    type: str
    auto_resolve_timeout: int | None
    acknowledgement_timeout: int | None
    created_at: datetime.datetime
    status: ServiceStatus
    last_incident_timestamp: datetime.datetime | None
    escalation_policy: ObjectRef
    # response_play: Optional[ObjectRef] = None
    teams: list[ObjectRef]
    integrations: list[ObjectRef]
    incident_urgency_rule: IncidentUrgencyRule
    support_hours: ObjectRef | None

    class Config:
        use_enum_values = True


class Vendor(ObjectRef):
    name: str
    type: str
    website_url: str
    logo_url: str | None
    thumbnail_url: str | None
    description: str | None
    integration_guide_url: str | None


class EmailFilterMode(str, Enum):
    ALL_EMAIL = 'all-email'
    OR_RULES_EMAIL = 'or-rules-email'
    AND_RULES_EMAIL = 'and-rules-email'


class EmailIncidentCreation(str, Enum):
    ON_NEW_EMAIL = 'on_new_email'
    ON_NEW_EMAIL_SUBJECT = 'on_new_email_subject'
    ONLY_IF_NO_OPEN_INCIDENTS = 'only_if_no_open_incidents'


# class EmailParser(BaseModel):
#     action: str
#     type


class EmailParsingFallback(str, Enum):
    OPEN_NEW_INCIDENT = 'open_new_incident'
    DISCARD = 'discard'


class EmailFilter(BaseModel):
    subject_mode: str
    subject_regex: str
    body_mode: str
    body_regex: str
    from_email_mode: str
    from_email_regex: str


class Integration(ObjectRef):
    """Integration defined for a service.
    """
    name: str
    id: str
    integration_key: str
    service: ObjectRef
    created_at: datetime.datetime
    vendor: ObjectRef | None
    integration_email: str | None
    email_incident_creation: EmailIncidentCreation | None
    email_filter_mode: EmailFilterMode | None
    # email_parsers: list[EmailParser]
    email_parsing_fallback: EmailParsingFallback | None
    email_filters: list[EmailFilter] | None

    class Config:
        use_enum_values = True


class UserRole(str, Enum):
    ADMIN = 'admin'
    LIMITED_USER = 'limited_user'
    OBSERVER = 'observer'
    OWNER = 'owner'
    READ_ONLY_USER = 'read_only_user'
    RESTRICTED_ACCESS = 'restricted_access'
    READ_ONLY_LIMITED_USER = 'read_only_limited_user'
    USER = 'user'


class User(ObjectRef):
    """PagerDuty user and their configuration settings.
    """
    email: EmailStr
    # time_zone: datetime.tzinfo
    time_zone: str
    color: str
    role: UserRole
    avatar_role: str | None
    description: str | None
    invitation_sent: bool | None
    job_title: str | None
    teams: list[ObjectRef] | None
    contact_methods: list[ObjectRef] | None
    notification_rules: list[ObjectRef] | None

    class Config:
        use_enum_values = True


class TeamMember(BaseModel):
    """Team member

    TeamMember isn't a first class object within PagerDuty. Hence, it cannot
    inherit frmo ObjectRef. The data returned is like this::
    ```json
    {
        "user": {
            "id": "P0XJYI9",
            "type": "user_reference",
            "summary": "Jane Doe",
            "self": "https://api.pagerduty.com/users/P0XJYI9",
            "html_url": "https://subdomain.pagerduty.com/users/P0XJYI9"
        },
        "role": "manager"
    }
    ```
    """
    user: ObjectRef
    role: str

    class Config:
        use_enum_values = True


class Runnability(str, Enum):
    SERVICES = 'services'
    TEAMS = 'teams'
    RESPONDERS = 'responders'


class ConferenceType(str, Enum):
    NONE = 'none'
    MANUAL = 'manual'
    ZOOM = 'zoom'


class ResponsePlay(ObjectRef):
    team: Team
    subscribers: list[ObjectRef]  # TODO: This should be User | Group?
    subscribers_message: str | None
    responders: list[ObjectRef] | None
    responders_message: str | None
    runnability: Runnability | None
    conference_number: str | None
    conference_url: str | None
    conference_type: ConferenceType | None


class ServiceOrchestrationStatus(BaseModel):
    active: bool


class Priority(ObjectRef):
    name: str
    description: str


class RefType(BaseModel):
    id: str  # Service Id
    self: str  # Service Ref URL
    type: str  # Reference type


class Condition(BaseModel):
    expression: str  # PCL expression


class Severity(str, Enum):
    INFO = 'info'
    ERROR = 'error'
    WARNING = 'warning'
    CRITICAL = 'critical'


class EventAction(str, Enum):
    TRIGGER = 'trigger'
    RESOLVE = 'resolve'


class VariableType(str, Enum):
    # only regex variable type is permitted
    REGEX = 'regex'


class Variable(BaseModel):
    """Defines a variable in service orchestration rules.
    """

    # name of the variable. eg: server_name
    name: str
    # Path to a field in an event, in dot-notation. eg: event.summary
    path: str
    # Type of variable operation.
    type: VariableType
    # A RE2 regular expression. If it contains capture groups, their
    # values will be extracted and appended together. If it contains no
    # capture groups, the whole match is used.
    # eg: `High CPUon (.*) server`
    value: str


class Extraction(BaseModel):
    """Defines an extraction into a variable in service orchesration rules.
    """
    # The PD-CEF field that will be set with the value from the template.
    # eg: event.summary
    target: str

    # A value that will be used to populate the target PD-CEF field.
    # You can include variables extracted from the payload by using string
    # interpolation.
    # eg: `High CPU on {{hostname}} server`
    template: str

    source: str | None
    regex: str | None


class Action(BaseModel):
    """Defines an action in service orchestration rules."""
    route_to: str | None  # route_to does not exist in catch_all actions

    # severity: Severity  # Severity of resulting alert
    severity: str | None  # TODO: issue to fix.

    # Suppress the resulting alert
    suppress: bool | None
    # Number of seconds to suspend the resuling alert before triggering
    suspend: int | None

    # Priority id for the priority defined for the account.
    priority: str | None
    # Add text as a note to the resulting incident
    annotate: str | None

    # Indicates whether the rule is disabled and would therefore not be evaluated.
    disabled: bool | None

    # Set whether the resulting alert status is trigger or resolve
    event_action: EventAction | None
    # Populate variables from event payloads and use those variables in
    # other event actions.
    variables: list[Variable] | None

    # use a template string and variables
    extractions: list[Extraction] | None

    class Config:
        use_enum_values = True


class Actions(BaseModel):
    actions: Action


class Rule(BaseModel):
    id: str
    label: str | None
    disabled: bool | None
    conditions: list[Condition]
    actions: Action

    class Config:
        use_enum_values = True


class RuleSet(BaseModel):
    id: str
    rules: list[Rule]

    class Config:
        use_enum_values = True


class ServiceOrchestration(BaseModel):
    """Defines a ServiceOrchestration rules for a service.
    """
    type: str
    parent: RefType
    version: str | None
    self: str
    updated_at: datetime.datetime | None
    updated_by: RefType | None
    created_at: datetime.datetime
    created_by: RefType | None
    sets: list[RuleSet] | None
    catch_all: Actions

    class Config:
        use_enum_values = True
