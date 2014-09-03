class Interactor:
    """ The player would be an example of an Interactor.  He can call a
    conversant's .speak() method. """

    def hail_conversant(self, conversant):
        conversation_step = conversant.speak(self, None)

    def respond_conversant(self, conversant, response_id):
        conversation_step = conversant.speak(self, response_id)
