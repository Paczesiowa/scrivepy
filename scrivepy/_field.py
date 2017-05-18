import tvu

from scrivepy._exceptions import InvalidResponse
from scrivepy._object import \
    enum_descriptor, scrive_descriptor, ScriveEnum, ScriveObject
from scrivepy._placement import Placement
from scrivepy._set import scrive_set_descriptor


class Field(ScriveObject):

    obligatory = scrive_descriptor(tvu.instance(bool), default_ctor_value=True,
                                   serialized_name=u'is_obligatory')
    placements = scrive_set_descriptor(Placement)

    @classmethod
    def _from_json_obj(cls, json):
        try:
            type_ = json[u'type']
        except KeyError:
            raise InvalidResponse('type missing')

        field_map = {u'checkbox': CheckboxField,
                     u'text': TextField,
                     u'signature': SignatureField,
                     u'name': NameField,
                     u'email': StandardField,
                     u'mobile': StandardField,
                     u'personal_number': StandardField,
                     u'company': StandardField,
                     u'company_number': StandardField}

        try:
            field_type = field_map[type_]
        except (KeyError, TypeError):
            err = (u'type must be checkbox|text|signature|name|email' +
                   u'|mobile|personal_number|company|company_number, not ' +
                   repr(type_))
            raise InvalidResponse(err)

        return super(Field, cls)._from_json_obj(json,
                                                class_override=field_type)


StandardFieldType = ScriveEnum('StandardFieldType',
                               ('email mobile personal_number ' +
                                'company company_number'))


class StandardField(Field):

    should_be_filled_by_sender = scrive_descriptor(tvu.instance(bool),
                                                   default_ctor_value=False)
    type = enum_descriptor(StandardFieldType, read_only=True)
    value = scrive_descriptor(tvu.tvus.Text, default_ctor_value=u'')


class type_descriptor(scrive_descriptor):

    def _init(self, obj, kwargs_dict):
        obj._type = self._default_ctor_value


class NameField(Field):

    order = scrive_descriptor(tvu.tvus.PositiveInt, default_ctor_value=1)
    should_be_filled_by_sender = scrive_descriptor(tvu.instance(bool),
                                                   default_ctor_value=False)
    type = type_descriptor(default_ctor_value=u'name')
    value = scrive_descriptor(tvu.tvus.Text, default_ctor_value=u'')


class TextField(Field):

    name = scrive_descriptor(tvu.tvus.NonEmptyText)
    should_be_filled_by_sender = scrive_descriptor(tvu.instance(bool),
                                                   default_ctor_value=False)
    type = type_descriptor(default_ctor_value=u'text')
    value = scrive_descriptor(tvu.tvus.Text, default_ctor_value=u'')


class SignatureField(Field):

    name = scrive_descriptor(tvu.tvus.NonEmptyText)
    type = type_descriptor(default_ctor_value=u'signature')


class CheckboxField(Field):

    checked = scrive_descriptor(tvu.instance(bool), default_ctor_value=False,
                                serialized_name=u'is_checked')
    name = scrive_descriptor(tvu.tvus.NonEmptyText)
    should_be_filled_by_sender = scrive_descriptor(tvu.instance(bool),
                                                   default_ctor_value=False)
    type = type_descriptor(default_ctor_value=u'checkbox')
