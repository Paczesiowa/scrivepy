import enum
from dateutil import parser as dateparser

import type_value_unifier as tvu
from scrivepy import _object, _signatory, _exceptions


scrive_property = _object.scrive_property


class SignatorySet(tvu.TypeValueUnifier):

    TYPES = (set,)

    def validate(self, value):
        for elem in value:
            if not isinstance(elem, _signatory.Signatory):
                self.error(u'set of Signatory objects')


class DocumentStatus(unicode, enum.Enum):
    preparation = u'Preparation'
    pending = u'Pending'
    closed = u'Closed'
    canceled = u'Canceled'
    timedout = u'Timedout'
    rejected = u'Rejected'
    error = u'DocumentError'


class Document(_object.ScriveObject):

    @tvu.validate_and_unify(title=tvu.instance(unicode),
                            number_of_days_to_sign=tvu.bounded_int(1, 90),
                            number_of_days_to_remind=
                            tvu.nullable(tvu.PositiveInt),
                            is_template=tvu.instance(bool),
                            signatories=SignatorySet)
    def __init__(self, title=u'', number_of_days_to_sign=14,
                 number_of_days_to_remind=None,
                 is_template=False, signatories=set()):
        super(Document, self).__init__()
        self._id = None
        self._title = title
        self._number_of_days_to_sign = number_of_days_to_sign
        self._number_of_days_to_remind = number_of_days_to_remind
        self._status = None
        self._modification_time = None
        self._creation_time = None
        self._signing_deadline = None
        self._autoremind_time = None
        self._current_sign_order = None
        self._is_template = is_template
        self._signatories = set(signatories)

    @classmethod
    def _from_json_obj(cls, json):
        try:
            signatories = \
                set([_signatory.Signatory._from_json_obj(signatory_json)
                     for signatory_json in json[u'signatories']])
            document = Document(title=json[u'title'],
                                number_of_days_to_sign=json[u'daystosign'],
                                number_of_days_to_remind=json[u'daystoremind'],
                                is_template=json[u'template'],
                                signatories=signatories)
            document._id = json[u'id']
            if json[u'time'] is not None:
                document._modification_time = dateparser.parse(json[u'time'])
            if json[u'ctime'] is not None:
                document._creation_time = dateparser.parse(json[u'ctime'])
            if json[u'timeouttime'] is not None:
                document._signing_deadline = \
                    dateparser.parse(json[u'timeouttime'])
            if json[u'autoremindtime'] is not None:
                document._autoremind_time = \
                    dateparser.parse(json[u'autoremindtime'])
            document._status = DocumentStatus(json[u'status'])
            document._current_sign_order = json[u'signorder']
            return document
        except (KeyError, TypeError, ValueError) as e:
            raise _exceptions.InvalidResponse(e)

    def _set_invalid(self):
        # invalidate signatories first, before getter stops working
        for signatory in self.signatories:
            signatory._set_invalid()
        super(Document, self)._set_invalid()

    def _set_read_only(self):
        super(Document, self)._set_read_only()
        for signatory in self.signatories:
            signatory._set_read_only()

    def _to_json_obj(self):
        return {u'title': self.title,
                u'daystosign': self.number_of_days_to_sign,
                u'daystoremind': self.number_of_days_to_remind,
                u'template': self.is_template,
                u'signatories': list(self.signatories)}

    @scrive_property
    def signatories(self):
        return iter(self._signatories)

    @signatories.setter
    @tvu.validate_and_unify(signatories=SignatorySet)
    def signatories(self, signatories):
        self._signatories = set(signatories)

    @scrive_property
    def id(self):
        return self._id

    @scrive_property
    def title(self):
        return self._title

    @title.setter
    @tvu.validate_and_unify(title=tvu.instance(unicode))
    def title(self, title):
        self._title = title

    @scrive_property
    def number_of_days_to_sign(self):
        return self._number_of_days_to_sign

    @number_of_days_to_sign.setter
    @tvu.validate_and_unify(number_of_days_to_sign=tvu.bounded_int(1, 90))
    def number_of_days_to_sign(self, number_of_days_to_sign):
        self._number_of_days_to_sign = number_of_days_to_sign

    @scrive_property
    def status(self):
        return self._status

    @scrive_property
    def modification_time(self):
        return self._modification_time

    @scrive_property
    def creation_time(self):
        return self._creation_time

    @scrive_property
    def signing_deadline(self):
        return self._signing_deadline

    @scrive_property
    def autoremind_time(self):
        return self._autoremind_time

    @scrive_property
    def current_sign_order(self):
        return self._current_sign_order

    @scrive_property
    def authentication_method(self):
        signatories = list(self.signatories)
        if not signatories:
            return u'mixed'

        # at least 1 signatory
        first_signatory = signatories.pop(0)
        result = first_signatory.authentication_method
        for signatory in signatories:
            if signatory.authentication_method != result:
                # signatories use various auth methods
                return u'mixed'
        # all signatories have the same auth method
        return result.value

    @scrive_property
    def invitation_delivery_method(self):
        signatories = list(self.signatories)
        if not signatories:
            return u'mixed'

        # at least 1 signatory
        first_signatory = signatories.pop(0)
        result = first_signatory.invitation_delivery_method
        for signatory in signatories:
            if signatory.invitation_delivery_method != result:
                # signatories use various invitation delivery methods
                return u'mixed'
        # all signatories have the same invitation delivery method
        return result.value

    @scrive_property
    def is_template(self):
        return self._is_template

    @is_template.setter
    @tvu.validate_and_unify(is_template=tvu.instance(bool))
    def is_template(self, is_template):
        self._is_template = is_template

    @scrive_property
    def number_of_days_to_remind(self):
        return self._number_of_days_to_remind

    @number_of_days_to_remind.setter
    @tvu.validate_and_unify(
        number_of_days_to_remind=tvu.nullable(tvu.PositiveInt))
    def number_of_days_to_remind(self, number_of_days_to_remind):
        self._number_of_days_to_remind = number_of_days_to_remind



# documentJSONV1 :: (MonadDB m, MonadThrow m, Log.MonadLog m, MonadIO m, AWS.AmazonMonad m) => (Maybe User) -> Bool -> Bool -> Bool ->  Maybe SignatoryLink -> Document -> m JSValue
# documentJSONV1 muser includeEvidenceAttachments forapi forauthor msl doc = do
#     file <- documentfileM doc
#     sealedfile <- documentsealedfileM doc
#     authorattachmentfiles <- mapM (dbQuery . GetFileByFileID . authorattachmentfile) (documentauthorattachments doc)
#     evidenceattachments <- if includeEvidenceAttachments then EvidenceAttachments.fetch doc else return []
#     runJSONGenT $ do
#       J.value "file" $ fmap fileJSON file
#       J.value "sealedfile" $ fmap fileJSON sealedfile
#       J.value "authorattachments" $ map fileJSON authorattachmentfiles
#       J.objects "evidenceattachments" $ for evidenceattachments $ \a -> do
#         J.value "name"     $ BSC.unpack $ EvidenceAttachments.name a
#         J.value "mimetype" $ BSC.unpack <$> EvidenceAttachments.mimetype a
#         J.value "downloadLink" $ show $ LinkEvidenceAttachment (documentid doc) (EvidenceAttachments.name a)
#       J.value "showheader" $ documentshowheader doc
#       J.value "showpdfdownload" $ documentshowpdfdownload doc
#       J.value "showrejectoption" $ documentshowrejectoption doc
#       J.value "showfooter" $ documentshowfooter doc
#       J.value "invitationmessage" $ documentinvitetext doc
#       J.value "confirmationmessage" $ documentconfirmtext doc
#       J.value "lang" $  case (getLang doc) of -- We keep some old lang codes for old integrations. We should drop it on new API release
#                              LANG_EN -> "gb"
#                              LANG_SV -> "sv"
#                              l -> codeFromLang l
#       J.objects "tags" $ for (Set.toList $ documenttags doc) $ \(DocumentTag n v) -> do
#                                     J.value "name"  n
#                                     J.value "value" v
#       J.value "apicallbackurl" $ documentapicallbackurl doc
#       J.value "saved" $ not (documentunsaveddraft doc)
#       J.value "deleted" $ fromMaybe False $ documentDeletedForUser doc <$> userid <$> muser
#       J.value "reallydeleted" $ fromMaybe False $ documentReallyDeletedForUser doc <$> userid <$>  muser
#       when (isJust muser) $
#         J.value "canperformsigning" $ userCanPerformSigningAction (userid $ fromJust muser) doc
#       J.value "objectversion" $ documentobjectversion doc
#       J.value "process" $ "Contract"
#       J.value "isviewedbyauthor" $ isSigLinkFor muser (getAuthorSigLink doc)
#       when (not $ forapi) $ do
#         J.value "canberestarted" $ isAuthor msl && ((documentstatus doc) `elem` [Canceled, Timedout, Rejected])
#         J.value "canbeprolonged" $ isAuthor msl && ((documentstatus doc) `elem` [Timedout])
#         J.value "canbecanceled" $ (isAuthor msl || fromMaybe False (useriscompanyadmin <$> muser)) && documentstatus doc == Pending
#         J.value "canseeallattachments" $ isAuthor msl || fromMaybe False (useriscompanyadmin <$> muser)
#       J.value "accesstoken" $ show (documentmagichash doc)
#       J.value "timezone" $ toString $ documenttimezonename doc

# instance FromJSValueWithUpdate Document where
#     fromJSValueWithUpdate mdoc = do
#         (invitationmessage :: Maybe (Maybe String)) <-  fromJSValueField "invitationmessage"
#         (confirmationmessage :: Maybe (Maybe String)) <-  fromJSValueField "confirmationmessage"
#         showheader <- fromJSValueField "showheader"
#         showpdfdownload <- fromJSValueField "showpdfdownload"
#         showrejectoption <- fromJSValueField "showrejectoption"
#         showfooter <- fromJSValueField "showfooter"
#         delivery <-  fromJSValueField "delivery"
#         lang <- fromJSValueField "lang"
#         mtimezone <- fromJSValueField "timezone"
#         tags <- fromJSValueFieldCustom "tags" $ fromJSValueCustomMany  fromJSValue
#         (apicallbackurl :: Maybe (Maybe String)) <- fromJSValueField "apicallbackurl"
#         saved <- fromJSValueField "saved"
#         authorattachments <- fromJSValueFieldCustom "authorattachments" $ fromJSValueCustomMany $ fmap (join . (fmap maybeRead)) $ (fromJSValueField "id")
#         return $ Just defaultValue {
#             documentlang  = updateWithDefaultAndField LANG_SV documentlang lang,
#             documentinvitetext = case (invitationmessage) of
#                                      Nothing -> fromMaybe "" $ documentinvitetext <$> mdoc
#                                      Just Nothing -> ""
#                                      Just (Just s) -> fromMaybe "" (resultToMaybe $ asValidInviteText s),
#             documentconfirmtext = case (confirmationmessage) of
#                                      Nothing -> fromMaybe "" $ documentconfirmtext <$> mdoc
#                                      Just Nothing -> ""
#                                      Just (Just s) -> fromMaybe "" (resultToMaybe $ asValidInviteText s),
#             documentshowheader = updateWithDefaultAndField True documentshowheader showheader,
#             documentshowpdfdownload = updateWithDefaultAndField True documentshowpdfdownload showpdfdownload,
#             documentshowrejectoption = updateWithDefaultAndField True documentshowrejectoption showrejectoption,
#             documentshowfooter = updateWithDefaultAndField True documentshowfooter showfooter,
#             documentauthorattachments = updateWithDefaultAndField [] documentauthorattachments (fmap AuthorAttachment <$> authorattachments),
#             documenttags = updateWithDefaultAndField Set.empty documenttags (Set.fromList <$> tags),
#             documentapicallbackurl = updateWithDefaultAndField Nothing documentapicallbackurl apicallbackurl,
#             documentunsaveddraft = updateWithDefaultAndField False documentunsaveddraft (fmap not saved),
#             documenttimezonename = updateWithDefaultAndField defaultTimeZoneName documenttimezonename (unsafeTimeZoneName <$> mtimezone)
#           }
#       where
#        updateWithDefaultAndField :: a -> (Document -> a) -> Maybe a -> a
#        updateWithDefaultAndField df uf mv = fromMaybe df (mv `mplus` (fmap uf mdoc))
