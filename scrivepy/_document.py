from tvu import instance, nullable
from tvu.tvus import NonEmptyText

from scrivepy._object import (
    ScriveEnum,
    ScriveObject,
    id_descriptor,
    remote_descriptor,
    scrive_descriptor)
from scrivepy._set import scrive_set_descriptor
from scrivepy._signatory import Signatory
from scrivepy._tvus import TimeTVU


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

DocumentStatus = ScriveEnum('DocumentStatus',
                            ('preparation pending closed canceled ' +
                             'timedout rejected document_error'))


class Document(ScriveObject):

    autoremind_time = remote_descriptor(nullable(TimeTVU),
                                        serialized_name=u'auto_remind_time')
    creation_time = remote_descriptor(TimeTVU, serialized_name=u'ctime')
    modification_time = remote_descriptor(TimeTVU, serialized_name=u'mtime')
    id = id_descriptor(preserve=True)
    parties = scrive_set_descriptor(Signatory)
    status = remote_descriptor(instance(DocumentStatus, enum=True),
                               default_ctor_value=DocumentStatus.preparation)
    title = scrive_descriptor(NonEmptyText, default_ctor_value=u'document')
    timeout_time = remote_descriptor(nullable(TimeTVU))
