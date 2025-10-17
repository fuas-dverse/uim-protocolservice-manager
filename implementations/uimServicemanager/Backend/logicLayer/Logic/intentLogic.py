from logicLayer.Interface import IintentDAL


class intentLogic:
    def __init__(self, intentDal: IintentDAL):
        self.intentDal = intentDal

    def getIntents(self):
        return self.intentDal.getIntents()

    def getIntentByID(self, ID):
        return self.intentDal.getIntentByID(ID)

    def addIntents(self, intentName, intentDescription, intentTags, rateLimit, price):
        return self.intentDal.addIntent(intentName, intentDescription, intentTags, rateLimit, price)

    def updateIntents(self, intentName, intentDescription, intentTags, rateLimit, price, Intents_ID):
        return self.intentDal.updateIntent(intentName, intentDescription, intentTags, rateLimit, price, Intents_ID)

    def deleteIntents(self, Intents_ID):
        return self.intentDal.deleteIntent(Intents_ID)
