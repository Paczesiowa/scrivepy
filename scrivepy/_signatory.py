from scrivepy import _object, _field, _exceptions
import enum
import type_value_unifier as tvu
from dateutil import parser as dateparser
    # J.value "authentication" $ authenticationJSON $ signatorylinkauthenticationmethod siglink

    # when (not (isPreparation doc) && forauthor && forapi && signatorylinkdeliverymethod siglink == APIDelivery) $ do
    #     J.value "signlink" $ show $ LinkSignDoc doc siglink

# instance FromJSValueWithUpdate SignatoryLink where
#     fromJSValueWithUpdate ms = do
#         mfields <- fromJSValueFieldCustom "fields" (fromJSValueManyWithUpdate $ fromMaybe [] (signatoryfields <$> ms))
#         authentication' <-  fromJSValueField "authentication"
#         delivery' <-  fromJSValueField "delivery"
#         case (mfields) of
#              (Just fields) -> return $ Just $ defaultValue {
#                   , signatorylinkauthenticationmethod = updateWithDefaultAndField StandardAuthentication signatorylinkauthenticationmethod authentication'
#                 }
#              _ -> return Nothing
scrive_property = _object.scrive_property


class FieldSet(tvu.TypeValueUnifier):

    TYPES = (set,)

    def validate(self, value):
        for elem in value:
            if not isinstance(elem, _field.Field):
                self.error(u'set of Field objects')


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


IDM = InvitationDeliveryMethod
CDM = ConfirmationDeliveryMethod

MaybeUnicode = tvu.nullable(tvu.instance(unicode))


class Signatory(_object.ScriveObject):

    @tvu.validate_and_unify(fields=FieldSet, sign_order=tvu.PositiveInt,
                            invitation_delivery_method=
                            tvu.instance(IDM, enum=True),
                            confirmation_delivery_method=
                            tvu.instance(CDM, enum=True),
                            viewer=tvu.instance(bool),
                            author=tvu.instance(bool),
                            sign_success_redirect_url=MaybeUnicode,
                            rejection_redirect_url=MaybeUnicode)
    def __init__(self, fields=set(), sign_order=1, viewer=False, author=False,
                 invitation_delivery_method=IDM.email,
                 confirmation_delivery_method=CDM.email,
                 sign_success_redirect_url=None,
                 rejection_redirect_url=None):
        super(Signatory, self).__init__()
        self._fields = set(fields)
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

    @classmethod
    def _from_json_obj(cls, json):
        try:
            fields = \
                set([_field.Field._from_json_obj(field_json)
                     for field_json in json[u'fields']])
            signatory = \
                Signatory(fields=fields, sign_order=json[u'signorder'],
                          invitation_delivery_method=IDM(json[u'delivery']),
                          confirmation_delivery_method=CDM(
                              json[u'confirmationdelivery']),
                          viewer=not json[u'signs'],
                          author=json[u'author'],
                          sign_success_redirect_url=
                          json[u'signsuccessredirect'],
                          rejection_redirect_url=json[u'rejectredirect'])
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
            return signatory
        except (KeyError, TypeError, ValueError) as e:
            raise _exceptions.InvalidResponse(e)

    def _set_invalid(self):
        # invalidate fields first, before getter stops working
        for field in self.fields:
            field._set_invalid()
        super(Signatory, self)._set_invalid()

    def _set_read_only(self):
        super(Signatory, self)._set_read_only()
        for field in self.fields:
            field._set_read_only()

    def _to_json_obj(self):
        return {u'fields': list(self.fields),
                u'signorder': self.sign_order,
                u'delivery': self.invitation_delivery_method.value,
                u'confirmationdelivery':
                self.confirmation_delivery_method.value,
                u'signs': not self.viewer,
                u'author': self.author,
                u'signsuccessredirect': self.sign_success_redirect_url,
                u'rejectredirect': self.rejection_redirect_url}

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
        return iter(self._fields)

    @fields.setter
    @tvu.validate_and_unify(fields=FieldSet)
    def fields(self, fields):
        self._fields = set(fields)

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
