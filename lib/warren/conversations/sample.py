from ..conversation import Conversation, ConversationNode, LinkNode

class Sample(Conversation):
    @staticmethod
    def can_say_messing_around(conversant, interactor):
        return True

    @staticmethod
    def root_should_jump(c, i):
        return None

    def __init__(self):
        super(Sample, self).__init__(
            ConversationNode(should_jump=self.root_should_jump,
                message="What do you think you're doing here?",
                links=[
                    LinkNode(offer_test=self.can_say_messing_around,
                        response="Messing around", next_node=ConversationNode(
                            message="I bet you think yourself clever."
                        )
                    )
                ]
            )
        )

Conversation.register(Conversation.SAMPLE, Sample)
