from warren.conversation import Conversation

class Willy(Conversation):

    @staticmethod
    def willy_has_coffee(c, i):
        return False

Conversation.register(Conversation.WILLY, Willy)
