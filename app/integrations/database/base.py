from abc import ABC, abstractmethod

class DatabaseIntegration(ABC):

    @abstractmethod
    def add_entity(self, entity_type, data):
        pass

    @abstractmethod
    def get_full_graph(self):
        pass

    @abstractmethod
    def get_entity(self, entity_id):
        pass

    @abstractmethod
    def get_all_entities(self):
        pass

    @abstractmethod
    def update_entity(self, entity_id, data):
        pass

    @abstractmethod
    def delete_entity(self, entity_id):
        pass

    @abstractmethod
    def add_relationship(self, data):
        pass

    @abstractmethod
    def search_entities(self, search_params):
        pass

    @abstractmethod
    def search_relationships(self, search_params):
        pass
