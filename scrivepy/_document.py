from tvu.tvus import NonEmptyText

from scrivepy._object import (
    ScriveEnum,
    ScriveObject,
    id_descriptor,
    scrive_descriptor)
from scrivepy._set import scrive_set_descriptor
from scrivepy._signatory import Signatory


Language = ScriveEnum('Language', {'english': u'en',
                                   'swedish': u'sv',
                                   'german': u'de',
                                   'french': u'fr',
                                   'italian': u'it',
                                   'spanish': u'es',
                                   'portuguese': u'pt',
                                   'dutch': u'nl',
                                   'danish': u'da',
                                   'norwegian': u'no',
                                   'greek': u'el',
                                   'finnish': u'fi',
                                   'estonian': u'et',
                                   'islandic': u'is',
                                   'lithuanian': u'lt',
                                   'latvian': u'lv'})


class Document(ScriveObject):

    id = id_descriptor(preserve=True)
    parties = scrive_set_descriptor(Signatory)
    title = scrive_descriptor(NonEmptyText, default_ctor_value=u'document')
