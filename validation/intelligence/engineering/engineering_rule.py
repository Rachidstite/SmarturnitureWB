from abc import ABC
from abc import abstractmethod


class EngineeringRule(
    ABC
):

    @abstractmethod
    def validate(
        self,
        panel_spec,
    ):
        pass
