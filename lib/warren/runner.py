from warren import version
import sys

from warren.resource import ResourceManager, ResourceFinder
from warren.entities.interactor import Interactor
from warren.entities.conversant import Conversant
from warren.conversation import Conversation
import warren.conversations

def main():
    print "Warren %s" % version
    print "Arguments: ", sys.argv

    ########################
    # Silly tests, move these.

    rf = ResourceFinder("/usr/local/share/warren") # XXX FIXME don't hardcode

    print "================="
    interactor = Interactor()
    conversant = Conversant(Conversation.get(Conversation.SAMPLE, None))
    print conversant.speak(interactor)
    print conversant.speak(interactor, -2)

    print "================="

    rm = ResourceManager(rf)
    willyconv = Conversation.get(Conversation.WILLY, rm)
    willy = Conversant(willyconv)

    print willy.speak(interactor)
    print willy.speak(interactor, -3)


    return 0
