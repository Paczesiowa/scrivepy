from scrivepy import _object, _field, _exceptions
import enum
import type_value_unifier as tvu
    # J.value "confirmationdelivery" $ signatorylinkconfirmationdeliverymethod siglink
    # J.value "signs" $ isSignatory siglink
    # J.value "author" $ isAuthor siglink
    # J.value "saved" $ isJust . maybesignatory $ siglink
    # J.value "datamismatch" $ signatorylinkelegdatamismatchmessage siglink
    # J.value "signdate" $ jsonDate $ signtime <$> maybesigninfo siglink
    # J.value "seendate" $ jsonDate $ signtime <$> maybeseeninfo siglink
    # J.value "readdate" $ jsonDate $ maybereadinvite siglink
    # J.value "rejecteddate" $ jsonDate rejectedDate
    # J.value "rejectionreason" $ signatorylinkrejectionreason siglink
    # J.value "status" $ show $ signatorylinkstatusclass siglink
    # J.objects "attachments" $ map signatoryAttachmentJSON (signatoryattachments siglink)
    # J.value "csv" $ csvcontents <$> signatorylinkcsvupload siglink
    # J.value "inpadqueue"  $ (fmap fst pq == Just (documentid doc)) && (fmap snd pq == Just (signatorylinkid siglink))
    # J.value "userid" $ show <$> maybesignatory siglink
    # J.value "signsuccessredirect" $ signatorylinksignredirecturl siglink
    # J.value "rejectredirect" $ signatorylinkrejectredirecturl siglink
    # J.value "authentication" $ authenticationJSON $ signatorylinkauthenticationmethod siglink

    # when (not (isPreparation doc) && forauthor && forapi && signatorylinkdeliverymethod siglink == APIDelivery) $ do
    #     J.value "signlink" $ show $ LinkSignDoc doc siglink
    # where
    #   rejectedDate = signatorylinkrejectiontime siglink

# instance FromJSValueWithUpdate SignatoryLink where
#     fromJSValueWithUpdate ms = do
#         author <- fromJSValueField "author"
#         signs  <- fromJSValueField "signs"
#         mfields <- fromJSValueFieldCustom "fields" (fromJSValueManyWithUpdate $ fromMaybe [] (signatoryfields <$> ms))
#         attachments <- fromJSValueField "attachments"
#         (csv :: Maybe (Maybe CSVUpload)) <- fromJSValueField "csv"
#         (sredirecturl :: Maybe (Maybe String)) <- fromJSValueField "signsuccessredirect"
#         (rredirecturl :: Maybe (Maybe String)) <- fromJSValueField "rejectredirect"
#         authentication' <-  fromJSValueField "authentication"
#         delivery' <-  fromJSValueField "delivery"
#         confirmationdelivery' <-  fromJSValueField "confirmationdelivery"
#         case (mfields) of
#              (Just fields) -> return $ Just $ defaultValue {
#                     signatorylinkid            = fromMaybe (unsafeSignatoryLinkID 0) (signatorylinkid <$> ms)
#                   , signatorysignorder     = updateWithDefaultAndField (SignOrder 1) signatorysignorder (SignOrder <$> signorder)
#                   , signatoryisauthor      = updateWithDefaultAndField False signatoryisauthor author
#                   , signatoryispartner     = updateWithDefaultAndField False signatoryispartner signs
#                   , signatorylinkcsvupload       = updateWithDefaultAndField Nothing signatorylinkcsvupload csv
#                   , signatoryattachments         = updateWithDefaultAndField [] signatoryattachments attachments
#                   , signatorylinksignredirecturl = updateWithDefaultAndField Nothing signatorylinksignredirecturl sredirecturl
#                   , signatorylinkrejectredirecturl = updateWithDefaultAndField Nothing signatorylinkrejectredirecturl rredirecturl
#                   , signatorylinkauthenticationmethod = updateWithDefaultAndField StandardAuthentication signatorylinkauthenticationmethod authentication'
#                   , signatorylinkconfirmationdeliverymethod = updateWithDefaultAndField EmailConfirmationDelivery signatorylinkconfirmationdeliverymethod confirmationdelivery'
#                 }
#              _ -> return Nothing
#       where
#        updateWithDefaultAndField :: a -> (SignatoryLink -> a) -> Maybe a -> a
#        updateWithDefaultAndField df uf mv = fromMaybe df (mv `mplus` (fmap uf ms))

# id, it's present in output, no point in sending it back in update(), should be immutable


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


IDM = InvitationDeliveryMethod


class Signatory(_object.ScriveObject):

    @tvu.validate_and_unify(fields=FieldSet, sign_order=tvu.PositiveInt,
                            invitation_delivery_method=
                            tvu.instance(IDM, enum=True))
    def __init__(self, fields=set(), sign_order=1,
                 invitation_delivery_method=IDM.email):
        super(Signatory, self).__init__()
        self._fields = set(fields)
        self._id = None
        self._current = None
        self._sign_order = sign_order
        self._undelivered_invitation = None
        self._undelivered_email_invitation = None
        self._undelivered_sms_invitation = None
        self._delivered_invitation = None
        self._invitation_delivery_method = invitation_delivery_method

    @classmethod
    def _from_json_obj(cls, json):
        try:
            fields = \
                set([_field.Field._from_json_obj(field_json)
                     for field_json in json[u'fields']])
            signatory = \
                Signatory(fields=fields, sign_order=json[u'signorder'],
                          invitation_delivery_method=IDM(json[u'delivery']))
            signatory._id = json[u'id']
            signatory._current = json[u'current']
            signatory._undelivered_invitation = json[u'undeliveredInvitation']
            signatory._undelivered_email_invitation = \
                json[u'undeliveredMailInvitation']
            signatory._undelivered_sms_invitation = \
                json[u'undeliveredSMSInvitation']
            signatory._delivered_invitation = \
                json[u'deliveredInvitation']
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
                u'delivery': self.invitation_delivery_method.value}

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
