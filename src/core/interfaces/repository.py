from abc import ABC, abstractmethod


class IRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int):
        pass

    @abstractmethod
    def find_all(self):
        pass

    @abstractmethod
    def create(self, **kwargs):
        pass

    @abstractmethod
    def update(self, id: int, **kwargs):
        pass

    @abstractmethod
    def delete(self, id: int):
        pass

    @abstractmethod
    def commit(self):
        pass
