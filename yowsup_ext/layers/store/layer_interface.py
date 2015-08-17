from yowsup.layers import YowLayerInterface

class StorageLayerInterface(YowLayerInterface):
    def getContact(self, jidOrNumber):
        contact = self._layer.getContact(jidOrNumber)
        if contact:
            return contact.toDict()

    def getContacts(self):
        return [contact.toDict() for contact in self._layer.getContacts()]

    def isContact(self, jidOrNumber):
        return self.getContact(jidOrNumber) is not None

    def addContact(self, jidOrNumber):
        return self._layer.addContact(jidOrNumber).toDict()

    def getUnreadReceivedMessages(self, jidOrNumber):
        return [message.toDict() for message in self._layer.getUnreadReceivedMessages(jidOrNumber)]

    def getUnackedReceivedMessages(self, jidOrNumber = None):
        return [message.toDict() for message in self._layer.getUnackedReceivedMessages(jidOrNumber)]

    def getMessages(self, jid, offset = 0, limit = 30):
        return self._layer.getMessages(jid, offset, limit)

    def getMessageByGenId(self, id_gen):
        return self._layer.getMessageByGenId(id_gen)

    def getConversation(self, jid):
        return self._layer.getConversation(jid)

    def reset(self):
        self._layer.reset()
