from enum import Enum


class ResultLevel(str, Enum):

    ERROR = "ERROR"

    WARNING = "WARNING"

    RECOMMENDATION = "RECOMMENDATION"

    OPTIMIZATION = "OPTIMIZATION"

    INFO = "INFO"
