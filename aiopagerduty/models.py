"""Data Models for PagerDuty API
"""

import datetime
from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, constr


class ObjectRef(BaseModel):
    id: str
    summary: str
    self: str  # url
    html_url: Optional[str]  # Vendor does not always have a html_url defined
    type: str


class SupportHours(BaseModel):
    type: str
    time_zone: str
    days_of_week: List[int]
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
    description: Optional[str]


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
    during_support_hours: Optional[IncidentUrgencyDefinition]
    outside_support_hours: Optional[IncidentUrgencyDefinition]


class Service(ObjectRef):
    """Service defined in PagerDuty
    """
    name: str
    description: Optional[str]
    type: str
    auto_resolve_timeout: Optional[int]
    acknowledgement_timeout: Optional[int]
    created_at: datetime.datetime
    status: ServiceStatus
    last_incident_timestamp: Optional[datetime.datetime]
    escalation_policy: ObjectRef
    # response_play: Optional[ObjectRef] = None
    teams: List[ObjectRef]
    integrations: List[ObjectRef]
    incident_urgency_rule: IncidentUrgencyRule
    support_hours: Optional[ObjectRef]

    class Config:
        use_enum_values = True


class Vendor(ObjectRef):
    name: str
    type: str
    website_url: str
    logo_url: Optional[str]
    thumbnail_url: Optional[str]
    description: Optional[str]
    integration_guide_url: Optional[str]


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
    vendor: Optional[ObjectRef]
    integration_email: Optional[str]
    email_incident_creation: Optional[EmailIncidentCreation]
    email_filter_mode: Optional[EmailFilterMode]
    # email_parsers: List[EmailParser]
    email_parsing_fallback: Optional[EmailParsingFallback]
    email_filters: Optional[List[EmailFilter]]

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


class UserInfo(BaseModel):
    name: constr(max_length=100)
    email: EmailStr
    # time_zone: datetime.tzinfo
    time_zome: Optional[str]
    description: Optional[str]
    job_title: Optional[str]
    color: Optional[str]
    role: Optional[UserRole]


class User(ObjectRef, UserInfo):
    """PagerDuty user and their configuration settings.
    """
    avatar_role: Optional[str]
    invitation_sent: Optional[bool]
    teams: Optional[List[ObjectRef]]
    contact_methods: Optional[List[ObjectRef]]
    notification_rules: Optional[List[ObjectRef]]

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
    subscribers: List[ObjectRef]  # TODO: This should be User | Group?
    subscribers_message: Optional[str]
    responders: Optional[List[ObjectRef]]
    responders_message: Optional[str]
    runnability: Optional[Runnability]
    conference_number: Optional[str]
    conference_url: Optional[str]
    conference_type: Optional[ConferenceType]


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

    source: Optional[str]
    regex: Optional[str]


class Action(BaseModel):
    """Defines an action in service orchestration rules."""
    route_to: Optional[str]  # route_to does not exist in catch_all actions

    # severity: Severity  # Severity of resulting alert
    severity: Optional[str]  # TODO: issue to fix.

    # Suppress the resulting alert
    suppress: Optional[bool]
    # Number of seconds to suspend the resuling alert before triggering
    suspend: Optional[int]

    # Priority id for the priority defined for the account.
    priority: Optional[str]
    # Add text as a note to the resulting incident
    annotate: Optional[str]

    # Indicates whether the rule is disabled and would therefore not be
    # evaluated.
    disabled: Optional[bool]

    # Set whether the resulting alert status is trigger or resolve
    event_action: Optional[EventAction]
    # Populate variables from event payloads and use those variables in
    # other event actions.
    variables: Optional[List[Variable]]

    # use a template string and variables
    extractions: Optional[List[Extraction]]

    class Config:
        use_enum_values = True


class Actions(BaseModel):
    actions: Action


class Rule(BaseModel):
    id: str
    label: Optional[str]
    disabled: Optional[bool]
    conditions: List[Condition]
    actions: Action

    class Config:
        use_enum_values = True


class RuleSet(BaseModel):
    id: str
    rules: List[Rule]

    class Config:
        use_enum_values = True


class ServiceOrchestration(BaseModel):
    """Defines a ServiceOrchestration rules for a service.
    """
    type: str
    parent: RefType
    version: Optional[str]
    self: str
    updated_at: Optional[datetime.datetime]
    updated_by: Optional[RefType]
    created_at: datetime.datetime
    created_by: Optional[RefType]
    sets: Optional[List[RuleSet]]
    catch_all: Actions

    class Config:
        use_enum_values = True


class HandoffNotifications(str, Enum):
    IF_HAS_SERVICES = 'if_has_services'
    ALWAYS = 'always'


class EscalationRule(BaseModel):
    id: str
    escalation_delay_in_minutes: int
    # The targets an incident should be assigned to upon reaching this rule.
    targets: List[ObjectRef]


class EscalationPolicy(ObjectRef):
    """Escalation Policy"""

    # The name of the escalation policy.
    name: str
    # Escalation policy description.
    description: Optional[str]
    # The number of times the escalation policy will repeat after reaching
    # the end of its escalation.
    # Default: 0
    num_loops: Optional[int]

    # Determines how on call handoff notifications will be sent for users on
    # the escalation policy. Defaults to "if_has_services".
    on_call_handoff_notifications: HandoffNotifications

    escalation_rules: List[EscalationRule]
    services: Optional[List[ObjectRef]]
    teams: Optional[List[ObjectRef]]

    class Config:
        use_enum_values = True
