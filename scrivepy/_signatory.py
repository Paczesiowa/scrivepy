from scrivepy import _object, _field, _exceptions
import type_value_unifier as tvu
    # J.value "signorder" $ unSignOrder $ signatorysignorder siglink
    # J.value "undeliveredInvitation" $ Undelivered == mailinvitationdeliverystatus siglink || Undelivered == smsinvitationdeliverystatus siglink
    # J.value "undeliveredMailInvitation" $ Undelivered == mailinvitationdeliverystatus siglink
    # J.value "undeliveredSMSInvitation" $  Undelivered == smsinvitationdeliverystatus siglink
    # J.value "deliveredInvitation" $ Delivered == mailinvitationdeliverystatus siglink || Delivered == smsinvitationdeliverystatus siglink
    # J.value "delivery" $ signatorylinkdeliverymethod siglink
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
#         signorder <- fromJSValueField "signorder"
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
#                   , signatorylinkdeliverymethod       = updateWithDefaultAndField EmailDelivery signatorylinkdeliverymethod delivery'
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


class Signatory(_object.ScriveObject):

    @tvu.validate_and_unify(fields=FieldSet)
    def __init__(self, fields=set()):
        super(Signatory, self).__init__()
        self._fields = set(fields)
        self._id = None
        self._current = None

    @classmethod
    def _from_json_obj(cls, json):
        try:
            fields = \
                set([_field.Field._from_json_obj(field_json)
                     for field_json in json[u'fields']])
            signatory = Signatory(fields=fields)
            signatory._id = json[u'id']
            signatory._current = json[u'current']
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
        return {u'fields': list(self.fields)}

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
