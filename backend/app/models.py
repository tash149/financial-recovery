from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class Institution(SQLModel, table=True):
    """Reference table: how to recognise an institution in signals, and which claim forms it uses."""

    id: str = Field(primary_key=True)
    canonical_name: str = Field(index=True)
    kind: str  # bank | insurer | mf_registrar | listed_company
    aliases: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    sms_sender_ids: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    email_domains: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    form_templates: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    registrar: str | None = None
    public_reference: dict = Field(default_factory=dict, sa_column=Column(JSON))
