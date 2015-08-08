from yowsup.layers import YowLayerInterface

class StorageLayerInterface(YowLayerInterface):
    def getContact(self, phoneOrJid):
        pass

    def getMessages(self, phoneOrJid, offset = 0, limit = 30):
        pass