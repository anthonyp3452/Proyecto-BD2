from abc import ABC, abstractmethod

class BaseDeDatos(ABC):
    @abstractmethod
    def conectar(self): pass
    @abstractmethod
    def insertar(self, query, params): pass
    @abstractmethod
    def consultar(self, query): pass
    @abstractmethod
    def actualizar(self, query, params): pass
    @abstractmethod
    def eliminar(self, query, params): pass
