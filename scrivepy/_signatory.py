import enum

from dateutil.parser import parse as time_parse
import tvu

from scrivepy._exceptions import Error, InvalidResponse
from scrivepy._field import Field
from scrivepy._file import RemoteFile
from scrivepy._object import scrive_property, scrive_descriptor, ScriveObject
from scrivepy._set import ScriveSet


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


class SignAuthenticationMethod(unicode, enum.Enum):
    standard = u'standard'
    swedish_bankid = u'se_bankid'
    sms_pin = u'sms_pin'


class ViewAuthenticationMethod(unicode, enum.Enum):
    standard = u'standard'
    swedish_bankid = u'se_bankid'
    norwegian_bankid = u'no_bankid'


# class SignatoryAttachment(ScriveObject):

#     @tvu(requested_name=tvu.tvus.NonEmptyText,
#          description=tvu.tvus.NonEmptyText)
#     def __init__(self, requested_name, description):
#         super(SignatoryAttachment, self).__init__()
#         self._requested_name = requested_name
#         self._description = description
#         self._file = None

#     @classmethod
#     def _from_json_obj(cls, json):
#         try:
#             signatory_attachment = \
#                 SignatoryAttachment(requested_name=json[u'name'],
#                                     description=json[u'description'])
#             file_json = json.get(u'file')
#             if file_json is not None:
#                 file_ = RemoteFile(id_=file_json[u'id'],
#                                    name=file_json[u'name'])
#                 signatory_attachment._file = file_
#             return signatory_attachment
#         except (KeyError, TypeError, ValueError) as e:
#             raise InvalidResponse(e)

#     def _to_json_obj(self):
#         return {u'name': self.requested_name,
#                 u'description': self.description}

#     def _set_api(self, api, document):
#         super(SignatoryAttachment, self)._set_api(api, document)
#         if self.file is not None:
#             self.file._set_api(api, document)

#     def _set_invalid(self):
#         if self.file is not None:
#             self.file._set_invalid()
#         super(SignatoryAttachment, self)._set_invalid()

#     def _set_read_only(self):
#         super(SignatoryAttachment, self)._set_read_only()
#         if self.file is not None:
#             self.file._set_read_only()

#     @scrive_property
#     def requested_name(self):
#         return self._requested_name

#     @requested_name.setter
#     @tvu(requested_name=tvu.tvus.NonEmptyText)
#     def requested_name(self, requested_name):
#         self._requested_name = requested_name

#     @scrive_property
#     def description(self):
#         return self._description

#     @description.setter
#     @tvu(description=tvu.tvus.NonEmptyText)
#     def description(self, description):
#         self._description = description

#     @scrive_property
#     def file(self):
#         return self._file


# MaybeUnicode = tvu.nullable(tvu.tvus.NonEmptyText)


class Signatory(ScriveObject):

    invitation_delivery = scrive_descriptor(tvu.instance(
        InvitationDeliveryMethod, enum=True))
    confirmation_delivery = scrive_descriptor(tvu.instance(
        ConfirmationDeliveryMethod, enum=True))
    sign_auth = scrive_descriptor(tvu.instance(
        SignAuthenticationMethod, enum=True))
    view_auth = scrive_descriptor(tvu.instance(
        ViewAuthenticationMethod, enum=True))
    viewer = scrive_descriptor(tvu.instance(bool))
    sign_order = scrive_descriptor(tvu.tvus.PositiveInt)
    sign_redirect_url = scrive_descriptor(tvu.tvus.Text)
    reject_redirect_url = scrive_descriptor(tvu.tvus.Text)
    allows_highlighting = scrive_descriptor(tvu.instance(bool))
    id = scrive_descriptor()
    user_id = scrive_descriptor()
    author = scrive_descriptor()
    view_time = scrive_descriptor()
    sign_time = scrive_descriptor()
    invitation_view_time = scrive_descriptor()
    rejection_time = scrive_descriptor()
    email_delivery_status = scrive_descriptor()
    mobile_delivery_status = scrive_descriptor()
    sign_url = scrive_descriptor()
    fields = scrive_descriptor()

    @tvu(sign_order=tvu.tvus.PositiveInt,
         invitation_delivery=tvu.instance(InvitationDeliveryMethod, enum=True),
         confirmation_delivery=tvu.instance(ConfirmationDeliveryMethod,
                                            enum=True),
         sign_auth=tvu.instance(SignAuthenticationMethod, enum=True),
         view_auth=tvu.instance(ViewAuthenticationMethod, enum=True),
         viewer=tvu.instance(bool), allows_highlighting=tvu.instance(bool),
         sign_redirect_url=tvu.tvus.Text, reject_redirect_url=tvu.tvus.Text)
    def __init__(self, sign_order=1, viewer=False,
                 invitation_delivery=InvitationDeliveryMethod.email,
                 confirmation_delivery=ConfirmationDeliveryMethod.email,
                 sign_auth=SignAuthenticationMethod.standard,
                 view_auth=ViewAuthenticationMethod.standard,
                 allows_highlighting=False,
                 sign_redirect_url=u'', reject_redirect_url=u''):
        super(Signatory, self).__init__()
        self._id = None
        self._user_id = None
        self._author = False
        self._email_delivery_status = u'unknown'
        self._mobile_delivery_status = u'unknown'
        self._sign_order = sign_order
        self._invitation_delivery = invitation_delivery
        self._confirmation_delivery = confirmation_delivery
        self._viewer = viewer
        self._allows_highlighting = allows_highlighting
        self._sign_time = None
        self._view_time = None
        self._invitation_view_time = None
        self._rejection_time = None
        self._sign_redirect_url = sign_redirect_url
        self._reject_redirect_url = reject_redirect_url
        self._sign_auth = sign_auth
        self._view_auth = view_auth
        self._sign_url = None
        self._fields = ScriveSet()
        self._fields._elem_validator = tvu.instance(Field)
        # self._attachments = ScriveSet()
        # self._attachments._elem_validator = tvu.instance(SignatoryAttachment)

    @classmethod
    def _from_json_obj(cls, json):
        try:
            fields = [Field._from_json_obj(field_json)
                      for field_json in json[u'fields']]
            # attachments = [SignatoryAttachment._from_json_obj(att_json)
            #                for att_json in json[u'attachments']]

            if json[u'delivery_method'] == u'email_mobile':
                invitation_delivery = InvitationDeliveryMethod.email_and_mobile
            else:
                invitation_delivery = \
                    InvitationDeliveryMethod(json[u'delivery_method'])

            if json[u'confirmation_delivery_method'] == u'email_mobile':
                confirmation_delivery = \
                    ConfirmationDeliveryMethod.email_and_mobile
            else:
                confirmation_delivery = ConfirmationDeliveryMethod(
                    json[u'confirmation_delivery_method'])

            if json[u'authentication_method_to_sign'] == u'se_bankid':
                sign_auth = SignAuthenticationMethod.swedish_bankid
            else:
                sign_auth = SignAuthenticationMethod(
                    json[u'authentication_method_to_sign'])

            if json[u'authentication_method_to_view'] == u'se_bankid':
                view_auth = ViewAuthenticationMethod.swedish_bankid
            elif json[u'authentication_method_to_view'] == u'no_bankid':
                view_auth = ViewAuthenticationMethod.norwegian_bankid
            else:
                view_auth = ViewAuthenticationMethod(
                    json[u'authentication_method_to_view'])

            signatory = \
                Signatory(sign_order=json[u'sign_order'],
                          invitation_delivery=invitation_delivery,
                          confirmation_delivery=confirmation_delivery,
                          sign_auth=sign_auth, view_auth=view_auth,
                          viewer=not json[u'is_signatory'],
                          allows_highlighting=json[u'allows_highlighting'],
                          sign_redirect_url=json[u'sign_success_redirect_url'],
                          reject_redirect_url=json[u'reject_redirect_url'])
            signatory.fields.update(fields)
            # signatory.attachments.update(attachments)
            signatory._email_delivery_status = json[u'email_delivery_status']
            signatory._mobile_delivery_status = json[u'mobile_delivery_status']
            signatory._id = json[u'id']
            signatory._user_id = json[u'user_id']
            signatory._author = json[u'is_author']
            if json[u'sign_time'] is not None:
                signatory._sign_time = time_parse(json[u'sign_time'])
            if json[u'seen_time'] is not None:
                signatory._view_time = time_parse(json[u'seen_time'])
            if json[u'read_invitation_time'] is not None:
                signatory._invitation_view_time = \
                    time_parse(json[u'read_invitation_time'])
            if json[u'rejected_time'] is not None:
                signatory._rejection_time = time_parse(json[u'rejected_time'])
            signatory._sign_url = json.get(u'api_delivery_url')
            return signatory
        except (KeyError, TypeError, ValueError) as e:
            raise InvalidResponse(e)

    def _to_json_obj(self):
        result = {u'fields': list(self.fields),
                  # u'attachments': list(self.attachments),
                  u'sign_order': self.sign_order,
                  u'delivery_method': self.invitation_delivery.value,
                  u'confirmation_delivery_method':
                  self.confirmation_delivery.value,
                  u'authentication_method_to_sign': self.sign_auth.value,
                  u'authentication_method_to_view': self.view_auth.value,
                  u'is_signatory': not self.viewer,
                  u'allows_highlighting': self.allows_highlighting,
                  u'sign_success_redirect_url': self.sign_redirect_url,
                  u'reject_redirect_url': self.reject_redirect_url}
        if self.id is not None:
            result[u'id'] = self.id
        return result

    def _set_invalid(self):
        # invalidate fields first, before getter stops working
        self.fields._set_invalid()
        # self.attachments._set_invalid()
        super(Signatory, self)._set_invalid()

    def _set_read_only(self):
        super(Signatory, self)._set_read_only()
        self.fields._set_read_only()
        # self.attachments._set_read_only()

    # def _set_api(self, api, document):
    #     super(Signatory, self)._set_api(api, document)
    #     for attachment in self.attachments:
    #         attachment._set_api(api, document)

    # @scrive_property
    # def fields(self):
    #     return self._fields

    # @scrive_property
    # def attachments(self):
    #     return self._attachments

    def absolute_sign_url(self):
        self._check_getter()
        if self._sign_url is None or self._api is None:
            return None
        proto = b'https' if self._api.https else b'http'
        return proto + b'://' + self._api.api_hostname + self._sign_url

    # @scrive_property
    # def full_name(self):
    #     fst_name_fields = filter(lambda f: f.name == SFT.first_name,
    #                              self.fields)
    #     last_name_fields = filter(lambda f: f.name == SFT.last_name,
    #                               self.fields)

    #     first_name_part = u''
    #     try:
    #         first_name_part = fst_name_fields[0].value
    #     except IndexError:
    #         pass

    #     last_name_part = u''
    #     try:
    #         last_name_part = last_name_fields[0].value
    #     except IndexError:
    #         pass

    #     if first_name_part != u'' and last_name_part != u'':
    #         return first_name_part + u' ' + last_name_part
    #     elif first_name_part != u'':
    #         return first_name_part
    #     elif last_name_part != u'':
    #         return last_name_part
    #     else:
    #         return u''

    # @full_name.setter
    # @tvu(full_name=tvu.tvus.Text)
    # def full_name(self, full_name):
    #     fst_name_fields = filter(lambda f: f.name == SFT.first_name,
    #                              self.fields)
    #     try:
    #         fst_name_field = fst_name_fields[0]
    #     except IndexError:
    #         fst_name_field = SF(name=SFT.first_name, value=u'')
    #         self.fields.add(fst_name_field)

    #     last_name_fields = filter(lambda f: f.name == SFT.last_name,
    #                               self.fields)
    #     try:
    #         last_name_field = last_name_fields[0]
    #     except IndexError:
    #         last_name_field = SF(name=SFT.last_name, value=u'')
    #         self.fields.add(last_name_field)

    #     if u' ' in full_name:
    #         name_parts = full_name.split(u' ')
    #         fst_name = name_parts[0]
    #         last_name = u' '.join(name_parts[1:])
    #     elif full_name != u' ':
    #         fst_name = full_name
    #         last_name = u''
    #     else:
    #         fst_name = u''
    #         last_name = u''

    #     fst_name_field.value = fst_name
    #     last_name_field.value = last_name
