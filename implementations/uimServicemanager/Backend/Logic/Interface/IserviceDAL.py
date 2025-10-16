from abc import ABC, abstractmethod

class IserviceDAL(ABC):
    @abstractmethod
    def getServices(self):
        pass
    @abstractmethod
    def getServiceByID(self, ID):
        pass

    @abstractmethod
    def addService(self, serviceName, serviceDescription, service_URL):
        pass
    @abstractmethod
    def updateService(self, serviceName, serviceDescription, service_URL, Service_ID):
        pass

    @abstractmethod
    def deleteService(self, Service_ID):
        pass