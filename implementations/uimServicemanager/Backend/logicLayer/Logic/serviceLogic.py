from logicLayer.Interface import IserviceDAL

class serviceLogic:
    def __init__(self, serviceDAL: IserviceDAL):
        self.serviceDAL = serviceDAL

    def getServices(self):
        return self.serviceDAL.getServices()

    def getServiceByID(self, ID):
        return self.serviceDAL.getServiceByID(ID)

    def addService(self, serviceName, serviceDescription, service_URL):
        return self.serviceDAL.addService(serviceName, serviceDescription, service_URL)

    def updateService(self, serviceName, serviceDescription, service_URL, Service_ID):
        return self.serviceDAL.updateService(serviceName, serviceDescription, service_URL, Service_ID)

    def deleteService(self, Service_ID):
        return self.serviceDAL.deleteService(Service_ID)