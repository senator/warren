import json

class ConversationError(ValueError):
    pass

def vivifier(obj):
    """ vivifier(obj) assists in loading conversation trees from JSON files. """

    if 'response' in obj:
        return LinkNode(**obj)
    else:
        return ConversationNode(**obj)

    if not obj.validate():
        raise ConversationError("Could not validate: " + obj)

class ConversationNode:
    """ A ConversationNode primarily represents something a conversant (NPC)
    can say.  Among other things, it can have references to LinkNodes,
    which are generally two things at once: 1) things an Interactor (player)
    can say back to the Conversant and 2) links to the next thing a conversant
    will say in response to #1. """

    def __init__(self, **kwargs):
        # First process any string names of functions into function refs ...
        for k in ['on_reach', 'should_jump']:
            if k in kwargs and not callable(kwargs[k]):
                kwargs[k] = getattr(kwargs['conversation'], kwargs[k])

        # ... then finish by setting attributes in our object based on keys in
        # the dict.
        for k in ['node_id', 'message', 'on_reach', 'links']:
            setattr(self, k, kwargs[k] if k in kwargs else None)

        # Special treatment for the should_jump attribute: make sure there's
        # always a method to run.
        if 'should_jump' in kwargs:
            self.should_jump = kwargs['should_jump']
        else:
            self.should_jump = lambda a, b: None

    def export(self, conversant, interactor):
        result = {'node_id': self.node_id, 'message': self.message}
        if self.links is not None:
            result['links'] = map(
                    lambda L: (L.next_node_id, L.response), filter(
                        lambda L: L.should_offer(conversant, interactor),
                        self.links))

        return result

    def validate(self):
        return self.message is not None or self.on_reach is not None


class LinkNode:
    def __init__(self, **kwargs):
        # First process any string names of functions into function refs ...
        if 'offer_test' in kwargs and not callable(kwargs['offer_test']):
            kwargs['offer_test'] = \
                getattr(kwargs['conversation'], kwargs['offer_test'])

        # ... then finish by setting attributes in our object based on keys in
        # the dict.
        for k in ['response', 'offer_test', 'next_node', 'jump']:
            setattr(self, k, kwargs[k] if k in kwargs else None)

    def should_offer(self, conversant, interactor):
        if self.offer_test is None:
            return True
        else:
            return self.offer_test(conversant, interactor)

    def validate(self):
        return self.response is not None

class Conversation(object):
    """ The class itself doubles as a container for instances. """

    SAMPLE = (0, None)
    WILLY = (1, "conv/willy.cct")

    conversation_classes = {}
    stash = {}

    @classmethod
    def register(cls, key, conversation_class):
        cls.conversation_classes[key[0]] = conversation_class

    @classmethod
    def get(cls, key, resource_manager):
        index, filename = key
        if filename is not None:
            # create singleton from file and let resource_manager stash it
            return resource_manager.get(
                filename,
                lambda f: cls.conversation_classes[index](json_file=f))
        else:
            # find singleton in our own stash, or instantiate, store, and return
            if index not in cls.stash:
                cls.stash[index] = cls.conversation_classes[index]()
            return cls.stash[index]

    def __init__(self, root=None, json_file=None):
        self.node_index = {}
        self.id_counter = -1

        if root is not None:
            self.root = root
        elif json_file is not None:
            self._from_json(json_file)

        self._index_nodes(self.root)

    def _from_json(self, f):

        def object_hook(o):
            o['conversation'] = self
            return vivifier(o)

        self.root = json.load(f, object_hook=object_hook)

    def _index_nodes(self, walk):
        if walk.node_id is None:
            walk.node_id = self.id_counter
            self.id_counter -= 1

        self.node_index[walk.node_id] = walk

        if walk.links:
            for link in walk.links:
                if link.next_node:
                    link.next_node_id = self._index_nodes(link.next_node)
                    link.next_node = None
                elif link.jump:
                    link.next_node_id = link.jump
                else:
                    raise ConversationError, "Link had neither next_node nor jump"

        return walk.node_id

