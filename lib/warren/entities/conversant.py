class Conversant:
    """ A conversant is a character-thing that speaks in a given conversation.
    It does not remember its place in the conversation. """

    def __init__(self, conversation):
        self.conversation = conversation

    def speak(self, interactor, response_id=None):
        if response_id is None:
            node = self.conversation.root
        else:
            node = self.conversation.node_index[response_id]

        if node.on_reach is not None:
            node.on_reach(self, interactor)

        should_jump = node.should_jump(self, interactor)
        if should_jump is not None:
            self.speak(interactor, should_jump)

        return node.export(self, interactor)

