import enum
import tvu

from scrivepy._exceptions import InvalidResponse
from scrivepy._object import scrive_descriptor, ScriveObject
from scrivepy._placement import Placement
from scrivepy._set import ScriveSet


class Field(ScriveObject):

    obligatory = scrive_descriptor(tvu.instance(bool))
    placements = scrive_descriptor()
    should_be_filled_by_sender = scrive_descriptor(tvu.instance(bool))
    type = scrive_descriptor()

    @tvu(obligatory=tvu.instance(bool),
         should_be_filled_by_sender=tvu.instance(bool))
    def __init__(self, obligatory=True, should_be_filled_by_sender=False):
        super(Field, self).__init__()
        self._obligatory = obligatory
        self._should_be_filled_by_sender = should_be_filled_by_sender
        self._placements = ScriveSet()
        self._placements._elem_validator = tvu.instance(Placement)

    def _set_invalid(self):
        # invalidate placements first, before getter stops working
        self.placements._set_invalid()
        super(Field, self)._set_invalid()

    def _set_read_only(self):
        super(Field, self)._set_read_only()
        self.placements._set_read_only()

    @classmethod
    def _from_json_obj(cls, json):
        try:
            type_ = json[u'type']
            obligatory = json[u'is_obligatory']
            placements = map(Placement._from_json_obj, json[u'placements'])

            # these may be none for some field types,
            # but in that case their ctors would not use it
            name = json.get(u'name')
            value = json.get(u'value')
            sbfbs = json.get(u'should_be_filled_by_sender')

            if type_ == u'name':
                order = json[u'order']
                field = NameField(obligatory=obligatory, value=value,
                                  order=order,
                                  should_be_filled_by_sender=sbfbs)
            elif type_ in StandardFieldType.__members__:
                field = StandardField(type_=StandardFieldType(type_),
                                      obligatory=obligatory, value=value,
                                      should_be_filled_by_sender=sbfbs)
            elif type_ == u'text':
                field = TextField(name=name, obligatory=obligatory,
                                  value=value,
                                  should_be_filled_by_sender=sbfbs)
            elif type_ == u'signature':
                signature = json[u'signature']
                field = SignatureField(name=name, obligatory=obligatory,
                                       signature=signature)
            elif type_ == u'checkbox':
                checked = json[u'is_checked']
                field = CheckboxField(name=name, checked=checked,
                                      obligatory=obligatory,
                                      should_be_filled_by_sender=sbfbs)
            else:
                raise InvalidResponse(u'bad field type: ' + repr(type_))

            field.placements.update(placements)

            return field
        except (KeyError, TypeError, ValueError) as e:
            raise InvalidResponse(e)

    def _to_json_obj(self):
        return {u'is_obligatory': self.obligatory,
                u'should_be_filled_by_sender': self.should_be_filled_by_sender,
                u'type': self.type,
                u'placements': list(self.placements)}


class StandardFieldType(unicode, enum.Enum):
    email = u'email'
    mobile = u'mobile'
    personal_number = u'personal_number'
    # company_name = u'company_name'
    company_number = u'company_number'


class StandardField(Field):

    value = scrive_descriptor(tvu.tvus.Text)

    @tvu(value=tvu.tvus.Text, obligatory=tvu.instance(bool),
         should_be_filled_by_sender=tvu.instance(bool),
         type_=tvu.instance(StandardFieldType, enum=True))
    def __init__(self, type_, obligatory=True, value=u'',
                 should_be_filled_by_sender=False):
        super(StandardField, self).__init__(
            obligatory=obligatory,
            should_be_filled_by_sender=should_be_filled_by_sender)
        self._type = type_.value
        self._value = value

    def _to_json_obj(self):
        result = super(StandardField, self)._to_json_obj()
        result[u'value'] = self.value
        return result


class NameField(Field):

    value = scrive_descriptor(tvu.tvus.Text)
    order = scrive_descriptor()

    @tvu(value=tvu.tvus.Text, obligatory=tvu.instance(bool),
         should_be_filled_by_sender=tvu.instance(bool),
         order=tvu.tvus.PositiveInt)
    def __init__(self, obligatory=True, value=u'', order=1,
                 should_be_filled_by_sender=False):
        super(NameField, self).__init__(
            obligatory=obligatory,
            should_be_filled_by_sender=should_be_filled_by_sender)
        self._type = u'name'
        self._value = value
        self._order = order

    def _to_json_obj(self):
        result = super(NameField, self)._to_json_obj()
        result[u'value'] = self.value
        result[u'order'] = self.order
        return result


class TextField(Field):

    value = scrive_descriptor(tvu.tvus.Text)
    name = scrive_descriptor(tvu.tvus.NonEmptyText)

    @tvu(value=tvu.tvus.Text, obligatory=tvu.instance(bool),
         should_be_filled_by_sender=tvu.instance(bool),
         name=tvu.tvus.NonEmptyText)
    def __init__(self, name, obligatory=True, value=u'',
                 should_be_filled_by_sender=False):
        super(TextField, self).__init__(
            obligatory=obligatory,
            should_be_filled_by_sender=should_be_filled_by_sender)
        self._type = u'text'
        self._value = value
        self._name = name

    def _to_json_obj(self):
        result = super(TextField, self)._to_json_obj()
        result[u'value'] = self.value
        result[u'name'] = self.name
        return result


class SignatureField(Field):

    signature = scrive_descriptor()
    name = scrive_descriptor(tvu.tvus.NonEmptyText)
    should_be_filled_by_sender = scrive_descriptor()

    @tvu(obligatory=tvu.instance(bool), name=tvu.tvus.NonEmptyText)
    def __init__(self, name, obligatory=True, signature=u''):
        super(SignatureField, self).__init__(
            obligatory=obligatory,
            should_be_filled_by_sender=False)
        self._type = u'signature'
        self._name = name
        self._signature = None

    def _to_json_obj(self):
        result = super(SignatureField, self)._to_json_obj()
        del result[u'should_be_filled_by_sender']
        result[u'signature'] = self.signature
        result[u'name'] = self.name
        return result


class CheckboxField(Field):

    checked = scrive_descriptor(tvu.instance(bool))
    name = scrive_descriptor(tvu.tvus.NonEmptyText)

    @tvu(name=tvu.tvus.NonEmptyText, checked=tvu.instance(bool),
         obligatory=tvu.instance(bool),
         should_be_filled_by_sender=tvu.instance(bool))
    def __init__(self, name, checked=False, obligatory=True,
                 should_be_filled_by_sender=False):
        super(CheckboxField, self).__init__(
            obligatory=obligatory,
            should_be_filled_by_sender=should_be_filled_by_sender)
        self._type = u'checkbox'
        self._checked = checked
        self._name = name

    def _to_json_obj(self):
        result = super(CheckboxField, self)._to_json_obj()
        result[u'is_checked'] = self.checked
        result[u'name'] = self.name
        return result
