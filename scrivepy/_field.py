import type_value_unifier as tvu
from scrivepy import _object, _field_placement, _exceptions


class PlacementSet(tvu.TypeValueUnifier):

    TYPES = (set,)

    def validate(self, value):
        for elem in value:
            if not isinstance(elem, _field_placement.FieldPlacement):
                self.error(u'set of FieldPlacement objects')


class Field(_object.ScriveObject):

    @tvu.validate_and_unify(value=tvu.instance(unicode),
                            obligatory=tvu.instance(bool),
                            should_be_filled_by_sender=tvu.instance(bool),
                            placements=PlacementSet)
    def __init__(self, value=u'', obligatory=True,
                 should_be_filled_by_sender=False, placements=set()):
        super(Field, self).__init__()
        self._json = {u'value': value,
                      u'closed': None,
                      u'obligatory': obligatory,
                      u'shouldbefilledbysender': should_be_filled_by_sender,
                      u'placements': set(placements)}

    def __str__(self):
        return u'%s(value=%s, %d placements)' % \
            (unicode(self.__class__.__name__),
             self.value, len(self.placements()))

    @classmethod
    def _from_json(cls, json):
        try:
            type_ = json[u'type']
            name = json[u'name']
            value = json[u'value']
            closed = json.get(u'closed')
            obligatory = json[u'obligatory']
            should_be_filled_by_sender = json[u'shouldbefilledbysender']
            placements = \
                set([_field_placement.FieldPlacement._from_json(placement_json)
                     for placement_json in json[u'placements']])

            if type_ == u'standard':
                if name == u'fstname':
                    field = FirstNameField(value=value)
                elif name == u'sndname':
                    field = LastNameField(value=value)
                elif name == u'email':
                    field = EmailField(value=value)
                elif name == u'mobile':
                    field = MobileNumberField(value=value)
                elif name == u'sigpersnr':
                    field = PersonalNumberField(value=value)
                elif name == u'sigco':
                    field = CompanyNameField(value=value)
                elif name == u'sigcompnr':
                    field = CompanyNumberField(value=value)
                else:
                    raise _exceptions.InvalidResponse(u'bad field name')
            elif type_ == u'custom':
                field = CustomField(name=name, value=value)
            elif type_ == u'signature':
                field = SignatureField(name=name)
                field._set_value(value)
            elif type_ == u'checkbox':
                field = CheckboxField(name=name,
                                      value=value.lower() == u'checked')
            else:
                raise _exceptions.InvalidResponse(u'bad field type')

            field.obligatory = obligatory
            field.should_be_filled_by_sender = should_be_filled_by_sender
            field.set_placements(placements)
            if closed is not None:
                field._set_closed(closed)
            return field
        except (KeyError, TypeError, ValueError) as e:
            raise _exceptions.InvalidResponse(e)

    def _invalid(self):
        super(Field, self)._invalid()
        for placement in self.placements():
            placement._invalid()

    def _read_only(self):
        super(Field, self)._invalid()
        for placement in self.placements():
            placement._read_only()

    def _to_json_obj(self):
        for placement in self.placements():
            placement._resolve_default_tip(self._default_placement_tip())
        return self._json

    def _default_placement_tip(self):
        return _field_placement.TipSide.right_tip

    @property
    def type(self):
        self._check_getter()
        return self._json[u'type']

    @property
    def name(self):
        self._check_getter()
        return self._json[u'name']

    @property
    def value(self):
        self._check_getter()
        return self._json[u'value']

    @value.setter
    @tvu.validate_and_unify(value=tvu.instance(unicode))
    def value(self, value):
        self._check_setter()
        self._json[u'value'] = value

    @property
    def closed(self):
        self._check_getter()
        return self._json[u'closed']

    @tvu.validate_and_unify(closed=tvu.instance(bool))
    def _set_closed(self, closed):
        self._check_setter()
        self._json[u'closed'] = closed

    @property
    def obligatory(self):
        self._check_getter()
        return self._json[u'obligatory']

    @obligatory.setter
    @tvu.validate_and_unify(value=tvu.instance(bool))
    def obligatory(self, obligatory):
        self._check_setter()
        self._json[u'obligatory'] = obligatory

    @property
    def should_be_filled_by_sender(self):
        self._check_getter()
        return self._json[u'shouldbefilledbysender']

    @should_be_filled_by_sender.setter
    @tvu.validate_and_unify(should_be_filled_by_sender=tvu.instance(bool))
    def should_be_filled_by_sender(self, should_be_filled_by_sender):
        self._check_setter()
        self._json[u'shouldbefilledbysender'] = should_be_filled_by_sender

    def placements(self):
        self._check_getter()
        return iter(self._json[u'placements'])

    @tvu.validate_and_unify(placements=PlacementSet)
    def set_placements(self, placements):
        self._check_setter()
        self._json[u'placements'] = set(placements)


class FirstNameField(Field):

    @tvu.validate_and_unify(value=tvu.instance(unicode),
                            obligatory=tvu.instance(bool),
                            should_be_filled_by_sender=tvu.instance(bool),
                            placements=PlacementSet)
    def __init__(self, value=u'', obligatory=True,
                 should_be_filled_by_sender=False, placements=set()):
        super(FirstNameField, self).__init__(
            value=value, obligatory=obligatory, placements=placements,
            should_be_filled_by_sender=should_be_filled_by_sender)
        self._json[u'type'] = u'standard'
        self._json[u'name'] = u'fstname'


class LastNameField(Field):

    @tvu.validate_and_unify(value=tvu.instance(unicode),
                            obligatory=tvu.instance(bool),
                            should_be_filled_by_sender=tvu.instance(bool),
                            placements=PlacementSet)
    def __init__(self, value=u'', obligatory=True,
                 should_be_filled_by_sender=False, placements=set()):
        super(LastNameField, self).__init__(
            value=value, obligatory=obligatory, placements=placements,
            should_be_filled_by_sender=should_be_filled_by_sender)
        self._json[u'type'] = u'standard'
        self._json[u'name'] = u'sndname'


class EmailField(Field):

    @tvu.validate_and_unify(value=tvu.instance(unicode),
                            obligatory=tvu.instance(bool),
                            should_be_filled_by_sender=tvu.instance(bool),
                            placements=PlacementSet)
    def __init__(self, value=u'', obligatory=True,
                 should_be_filled_by_sender=False, placements=set()):
        super(EmailField, self).__init__(
            value=value, obligatory=obligatory, placements=placements,
            should_be_filled_by_sender=should_be_filled_by_sender)
        self._json[u'type'] = u'standard'
        self._json[u'name'] = u'email'


class MobileNumberField(Field):

    @tvu.validate_and_unify(value=tvu.instance(unicode),
                            obligatory=tvu.instance(bool),
                            should_be_filled_by_sender=tvu.instance(bool),
                            placements=PlacementSet)
    def __init__(self, value=u'', obligatory=False,
                 should_be_filled_by_sender=False, placements=set()):
        super(MobileNumberField, self).__init__(
            value=value, obligatory=obligatory, placements=placements,
            should_be_filled_by_sender=should_be_filled_by_sender)
        self._json[u'type'] = u'standard'
        self._json[u'name'] = u'mobile'


class PersonalNumberField(Field):

    @tvu.validate_and_unify(value=tvu.instance(unicode),
                            obligatory=tvu.instance(bool),
                            should_be_filled_by_sender=tvu.instance(bool),
                            placements=PlacementSet)
    def __init__(self, value=u'', obligatory=True,
                 should_be_filled_by_sender=False, placements=set()):
        super(PersonalNumberField, self).__init__(
            value=value, obligatory=obligatory, placements=placements,
            should_be_filled_by_sender=should_be_filled_by_sender)
        self._json[u'type'] = u'standard'
        self._json[u'name'] = u'sigpersnr'


class CompanyNameField(Field):

    @tvu.validate_and_unify(value=tvu.instance(unicode),
                            obligatory=tvu.instance(bool),
                            should_be_filled_by_sender=tvu.instance(bool),
                            placements=PlacementSet)
    def __init__(self, value=u'', obligatory=False,
                 should_be_filled_by_sender=False, placements=set()):
        super(CompanyNameField, self).__init__(
            value=value, obligatory=obligatory, placements=placements,
            should_be_filled_by_sender=should_be_filled_by_sender)
        self._json[u'type'] = u'standard'
        self._json[u'name'] = u'sigco'


class CompanyNumberField(Field):

    @tvu.validate_and_unify(value=tvu.instance(unicode),
                            obligatory=tvu.instance(bool),
                            should_be_filled_by_sender=tvu.instance(bool),
                            placements=PlacementSet)
    def __init__(self, value=u'', obligatory=True,
                 should_be_filled_by_sender=False, placements=set()):
        super(CompanyNumberField, self).__init__(
            value=value, obligatory=obligatory, placements=placements,
            should_be_filled_by_sender=should_be_filled_by_sender)
        self._json[u'type'] = u'standard'
        self._json[u'name'] = u'sigcompnr'


class CustomField(Field):

    @tvu.validate_and_unify(name=tvu.instance(unicode),
                            value=tvu.instance(unicode),
                            obligatory=tvu.instance(bool),
                            should_be_filled_by_sender=tvu.instance(bool),
                            placements=PlacementSet)
    def __init__(self, name, value=u'', obligatory=True,
                 should_be_filled_by_sender=False, placements=set()):
        super(CustomField, self).__init__(
            value=value, obligatory=obligatory, placements=placements,
            should_be_filled_by_sender=should_be_filled_by_sender)
        self._json[u'type'] = u'custom'
        self._json[u'name'] = name

    @property
    def name(self):
        self._check_getter()
        return self._json[u'name']

    @name.setter
    @tvu.validate_and_unify(name=tvu.instance(unicode))
    def name(self, name):
        self._check_setter()
        self._json[u'name'] = name


class SignatureField(Field):

    @tvu.validate_and_unify(name=tvu.instance(unicode),
                            obligatory=tvu.instance(bool),
                            should_be_filled_by_sender=tvu.instance(bool),
                            placements=PlacementSet)
    def __init__(self, name, obligatory=True,
                 should_be_filled_by_sender=False, placements=set()):
        super(SignatureField, self).__init__(
            value=u'', obligatory=obligatory, placements=placements,
            should_be_filled_by_sender=should_be_filled_by_sender)
        self._json[u'type'] = u'signature'
        self._json[u'name'] = name

    @property
    def name(self):
        self._check_getter()
        return self._json[u'name']

    @name.setter
    @tvu.validate_and_unify(name=tvu.instance(unicode))
    def name(self, name):
        self._check_setter()
        self._json[u'name'] = name

    @property
    def value(self):
        self._check_getter()
        return self._json[u'value']

    @tvu.validate_and_unify(value=tvu.instance(unicode))
    def _set_value(self, value):
        self._check_setter()
        self._json[u'value'] = value


class CheckboxField(Field):

    @tvu.validate_and_unify(name=tvu.instance(unicode),
                            value=tvu.instance(bool),
                            obligatory=tvu.instance(bool),
                            should_be_filled_by_sender=tvu.instance(bool),
                            placements=PlacementSet)
    def __init__(self, name, value=False, obligatory=False,
                 should_be_filled_by_sender=False, placements=set()):
        super(CheckboxField, self).__init__(
            value=u'CHECKED' if value else u'', obligatory=obligatory,
            placements=placements,
            should_be_filled_by_sender=should_be_filled_by_sender)
        self._json[u'type'] = u'checkbox'
        self._json[u'name'] = name

    def _default_placement_tip(self):
        return _field_placement.TipSide.left_tip

    @property
    def name(self):
        self._check_getter()
        return self._json[u'name']

    @name.setter
    @tvu.validate_and_unify(name=tvu.instance(unicode))
    def name(self, name):
        self._check_setter()
        self._json[u'name'] = name

    @property
    def value(self):
        self._check_getter()
        return self._json[u'value'].lower() == u'checked'

    @value.setter
    @tvu.validate_and_unify(value=tvu.instance(bool))
    def value(self, value):
        self._check_setter()
        self._json[u'value'] = u'CHECKED' if value else u''
