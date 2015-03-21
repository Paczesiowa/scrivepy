import enum
from dateutil import parser as dateparser

import type_value_unifier as tvu
from scrivepy import _object, _field, _exceptions, _set, _file


scrive_property = _object.scrive_property


class InvitationDeliveryMethod(unicode, enum.Enum):
    email = u'email'
    pad = u'pad'
    api = u'api'
    mobile = u'mobile'
    email_and_mobile = u'email_mobile'


class ConfirmationDeliveryMethod(unicode, enum.Enum):
    email = u'email'
    mobile = u'mobile'
    email_and_mobile = u'email_mobile'
    none = u'none'


class AuthenticationMethod(unicode, enum.Enum):
    standard = u'standard'
    eleg = u'eleg'
    sms_pin = u'sms_pin'


class SignatoryAttachment(_object.ScriveObject):

    @tvu.validate_and_unify(requested_name=tvu.NonEmptyUnicode,
                            description=tvu.NonEmptyUnicode)
    def __init__(self, requested_name, description):
        super(SignatoryAttachment, self).__init__()
        self._requested_name = requested_name
        self._description = description
        self._file = None

    @classmethod
    def _from_json_obj(cls, json):
        try:
            signatory_attachment = \
                SignatoryAttachment(requested_name=json[u'name'],
                                    description=json[u'description'])
            file_json = json.get(u'file')
            if file_json is not None:
                file_ = _file.RemoteFile(id_=file_json[u'id'],
                                         name=file_json[u'name'])
                signatory_attachment._file = file_
            return signatory_attachment
        except (KeyError, TypeError, ValueError) as e:
            raise _exceptions.InvalidResponse(e)

    def _to_json_obj(self):
        return {u'name': self.requested_name,
                u'description': self.description}

    def _set_api(self, api, document):
        super(SignatoryAttachment, self)._set_api(api, document)
        if self._file is not None:
            self._file._set_api(api, document)

    @scrive_property
    def requested_name(self):
        return self._requested_name

    @requested_name.setter
    @tvu.validate_and_unify(requested_name=tvu.NonEmptyUnicode)
    def requested_name(self, requested_name):
        self._requested_name = requested_name

    @scrive_property
    def description(self):
        return self._description

    @description.setter
    @tvu.validate_and_unify(description=tvu.NonEmptyUnicode)
    def description(self, description):
        self._description = description

    @scrive_property
    def file(self):
        return self._file


IDM = InvitationDeliveryMethod
CDM = ConfirmationDeliveryMethod
AM = AuthenticationMethod

MaybeUnicode = tvu.nullable(tvu.instance(unicode))


class Signatory(_object.ScriveObject):

    @tvu.validate_and_unify(sign_order=tvu.PositiveInt,
                            invitation_delivery_method=
                            tvu.instance(IDM, enum=True),
                            confirmation_delivery_method=
                            tvu.instance(CDM, enum=True),
                            authentication_method=
                            tvu.instance(AM, enum=True),
                            viewer=tvu.instance(bool),
                            author=tvu.instance(bool),
                            sign_success_redirect_url=MaybeUnicode,
                            rejection_redirect_url=MaybeUnicode)
    def __init__(self, sign_order=1, viewer=False, author=False,
                 invitation_delivery_method=IDM.email,
                 confirmation_delivery_method=CDM.email,
                 authentication_method=AM.standard,
                 sign_success_redirect_url=None,
                 rejection_redirect_url=None):
        super(Signatory, self).__init__()
        self._id = None
        self._current = None
        self._sign_order = sign_order
        self._undelivered_invitation = None
        self._undelivered_email_invitation = None
        self._undelivered_sms_invitation = None
        self._delivered_invitation = None
        self._has_account = None
        self._invitation_delivery_method = invitation_delivery_method
        self._confirmation_delivery_method = confirmation_delivery_method
        self._viewer = viewer
        self._author = author
        self._eleg_mismatch_message = None
        self._sign_time = None
        self._view_time = None
        self._invitation_view_time = None
        self._rejection_time = None
        self._rejection_message = None
        self._sign_success_redirect_url = sign_success_redirect_url
        self._rejection_redirect_url = rejection_redirect_url
        self._authentication_method = authentication_method
        self._sign_url = None
        self._fields = _set.ScriveSet()
        self._fields._elem_validator = tvu.instance(_field.Field)
        self._attachments = _set.ScriveSet()
        self._attachments._elem_validator = tvu.instance(SignatoryAttachment)

    @classmethod
    def _from_json_obj(cls, json):
        try:
            fields = [_field.Field._from_json_obj(field_json)
                      for field_json in json[u'fields']]
            attachments = [SignatoryAttachment._from_json_obj(att_json)
                           for att_json in json[u'attachments']]
            signatory = \
                Signatory(sign_order=json[u'signorder'],
                          invitation_delivery_method=IDM(json[u'delivery']),
                          confirmation_delivery_method=CDM(
                              json[u'confirmationdelivery']),
                          authentication_method=AM(json[u'authentication']),
                          viewer=not json[u'signs'],
                          author=json[u'author'],
                          sign_success_redirect_url=
                          json[u'signsuccessredirect'],
                          rejection_redirect_url=json[u'rejectredirect'])
            signatory.fields.update(fields)
            signatory.attachments.update(attachments)
            signatory._id = json[u'id']
            signatory._current = json[u'current']
            signatory._undelivered_invitation = json[u'undeliveredInvitation']
            signatory._undelivered_email_invitation = \
                json[u'undeliveredMailInvitation']
            signatory._undelivered_sms_invitation = \
                json[u'undeliveredSMSInvitation']
            signatory._delivered_invitation = \
                json[u'deliveredInvitation']
            signatory._has_account = \
                json[u'saved']
            signatory._eleg_mismatch_message = \
                json[u'datamismatch']
            if json[u'signdate'] is not None:
                signatory._sign_time = dateparser.parse(json[u'signdate'])
            if json[u'seendate'] is not None:
                signatory._view_time = dateparser.parse(json[u'seendate'])
            if json[u'readdate'] is not None:
                signatory._invitation_view_time = \
                    dateparser.parse(json[u'readdate'])
            if json[u'rejecteddate'] is not None:
                signatory._rejection_time = \
                    dateparser.parse(json[u'rejecteddate'])
            signatory._rejection_message = json[u'rejectionreason']
            signatory._sign_url = json.get(u'signlink')
            return signatory
        except (KeyError, TypeError, ValueError) as e:
            raise _exceptions.InvalidResponse(e)

    def _set_invalid(self):
        # invalidate fields first, before getter stops working
        self.fields._set_invalid()
        self.attachments._set_invalid()
        super(Signatory, self)._set_invalid()

    def _set_read_only(self):
        super(Signatory, self)._set_read_only()
        self.fields._set_read_only()
        self.attachments._set_read_only()

    def _set_api(self, api, document):
        super(Signatory, self)._set_api(api, document)
        for attachment in self.attachments:
            attachment._set_api(api, document)

    def _to_json_obj(self):
        result = {u'fields': list(self.fields),
                  u'attachments': list(self.attachments),
                  u'signorder': self.sign_order,
                  u'delivery': self.invitation_delivery_method.value,
                  u'confirmationdelivery':
                  self.confirmation_delivery_method.value,
                  u'authentication': self.authentication_method.value,
                  u'signs': not self.viewer,
                  u'author': self.author,
                  u'signsuccessredirect': self.sign_success_redirect_url,
                  u'rejectredirect': self.rejection_redirect_url}
        if self.id is not None:
            result[u'id'] = self.id
        return result

#     @property
#     def status(self):
# documents.status                                == DocumentError => SCError           ~ "problem"
# documents.status                                == Preparation   => SCDraft           ~ "draft"
# signatory_links.sign_time                       != NULL          => SCSigned          ~ "signed"
# documents.status                                == Canceled      => SCCancelled       ~ "cancelled"
# documents.status                                == Timedout      => SCTimedout        ~ "timeouted"
# documents.status                                == Rejected      => SCRejected        ~ "rejected"
# signatory_links.seen_time                       != NULL          => SCOpened          ~ "opened"
# signatory_links.read_invitation                 != NULL          => SCRead            ~ "read"
# signatory_links.mail_invitation_delivery_status == Undelivered   => SCDeliveryProblem ~ "deliveryproblem"
# signatory_links.sms_invitation_delivery_status  == Undelivered   => SCDeliveryProblem ~ "deliveryproblem"
# signatory_links.mail_invitation_delivery_status == Delivered     => SCDelivered       ~ "delivered"
# signatory_links.sms_invitation_delivery_status  == Delivered     => SCDelivered       ~ "delivered"
# otherwise                                                        => SCSent            ~ "sent"

    @scrive_property
    def fields(self):
        return self._fields

    @scrive_property
    def attachments(self):
        return self._attachments

    @scrive_property
    def id(self):
        return self._id

    @scrive_property
    def current(self):
        return self._current

    @scrive_property
    def sign_order(self):
        return self._sign_order

    @sign_order.setter
    @tvu.validate_and_unify(sign_order=tvu.PositiveInt)
    def sign_order(self, sign_order):
        self._sign_order = sign_order

    @scrive_property
    def undelivered_invitation(self):
        return self._undelivered_invitation

    @scrive_property
    def undelivered_email_invitation(self):
        return self._undelivered_email_invitation

    @scrive_property
    def undelivered_sms_invitation(self):
        return self._undelivered_sms_invitation

    @scrive_property
    def delivered_invitation(self):
        return self._delivered_invitation

    @scrive_property
    def invitation_delivery_method(self):
        return self._invitation_delivery_method

    @invitation_delivery_method.setter
    @tvu.validate_and_unify(
        invitation_delivery_method=tvu.instance(IDM, enum=True))
    def invitation_delivery_method(self, invitation_delivery_method):
        self._invitation_delivery_method = invitation_delivery_method

    @scrive_property
    def confirmation_delivery_method(self):
        return self._confirmation_delivery_method

    @confirmation_delivery_method.setter
    @tvu.validate_and_unify(
        confirmation_delivery_method=tvu.instance(CDM, enum=True))
    def confirmation_delivery_method(self, confirmation_delivery_method):
        self._confirmation_delivery_method = confirmation_delivery_method

    @scrive_property
    def viewer(self):
        return self._viewer

    @viewer.setter
    @tvu.validate_and_unify(viewer=tvu.instance(bool))
    def viewer(self, viewer):
        self._viewer = viewer

    @scrive_property
    def author(self):
        return self._author

    @author.setter
    @tvu.validate_and_unify(author=tvu.instance(bool))
    def author(self, author):
        self._author = author

    @scrive_property
    def has_account(self):
        return self._has_account

    @scrive_property
    def eleg_mismatch_message(self):
        return self._eleg_mismatch_message

    @scrive_property
    def sign_time(self):
        return self._sign_time

    @scrive_property
    def view_time(self):
        return self._view_time

    @scrive_property
    def invitation_view_time(self):
        return self._invitation_view_time

    @scrive_property
    def rejection_time(self):
        return self._rejection_time

    @scrive_property
    def rejection_message(self):
        return self._rejection_message

    @scrive_property
    def sign_success_redirect_url(self):
        return self._sign_success_redirect_url

    @sign_success_redirect_url.setter
    @tvu.validate_and_unify(sign_success_redirect_url=MaybeUnicode)
    def sign_success_redirect_url(self, sign_success_redirect_url):
        self._sign_success_redirect_url = sign_success_redirect_url

    @scrive_property
    def rejection_redirect_url(self):
        return self._rejection_redirect_url

    @rejection_redirect_url.setter
    @tvu.validate_and_unify(rejection_redirect_url=MaybeUnicode)
    def rejection_redirect_url(self, rejection_redirect_url):
        self._rejection_redirect_url = rejection_redirect_url

    @scrive_property
    def authentication_method(self):
        return self._authentication_method

    @authentication_method.setter
    @tvu.validate_and_unify(
        authentication_method=tvu.instance(AM, enum=True))
    def authentication_method(self, authentication_method):
        self._authentication_method = authentication_method

    @scrive_property
    def sign_url(self):
        return self._sign_url
