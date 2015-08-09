from yowsup.layers import YowLayerInterface

class StorageLayerInterface(YowLayerInterface):
    def getContact(self, jid):
        pass

    def getMessages(self, jid, offset = 0, limit = 30):
        return self._layer.getMessages(jid, offset, limit)

    def getConversation(self, jid):
        return self._layer.getConversation(jid)

    def reset(self):
        self._layer.reset()