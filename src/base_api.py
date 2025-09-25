from abc import ABC, abstractmethod


class BaseAPI(ABC):

    @abstractmethod
    def load_employers(self, keyword):
        pass
