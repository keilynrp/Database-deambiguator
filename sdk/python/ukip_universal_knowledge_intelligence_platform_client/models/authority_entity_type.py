from enum import Enum


class AuthorityEntityType(str, Enum):
    CONCEPT = "concept"
    GENERAL = "general"
    INSTITUTION = "institution"
    ORGANIZATION = "organization"
    PERSON = "person"

    def __str__(self) -> str:
        return str(self.value)
