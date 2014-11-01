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


class Document(_object.ScriveObject):

    @tvu.validate_and_unify(signatories=SignatorySet)
    def __init__(self, signatories=set()):
        super(Document, self).__init__()
        self._signatories = set(signatories)

    @classmethod
    def _from_json_obj(cls, json):
        try:
            signatories = \
                set([_signatory.Signatory._from_json_obj(signatory_json)
                     for signatory_json in json[u'signatories']])
            document = Document(signatories=signatories)
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
        return {u'signatories': list(self.signatories)}

    @scrive_property
    def signatories(self):
        return iter(self._signatories)

    @signatories.setter
    @tvu.validate_and_unify(signatories=SignatorySet)
    def signatories(self, signatories):
        self._signatories = set(signatories)

# documentJSONV1 :: (MonadDB m, MonadThrow m, Log.MonadLog m, MonadIO m, AWS.AmazonMonad m) => (Maybe User) -> Bool -> Bool -> Bool ->  Maybe SignatoryLink -> Document -> m JSValue
# documentJSONV1 muser includeEvidenceAttachments forapi forauthor msl doc = do
#     file <- documentfileM doc
#     sealedfile <- documentsealedfileM doc
#     authorattachmentfiles <- mapM (dbQuery . GetFileByFileID . authorattachmentfile) (documentauthorattachments doc)
#     evidenceattachments <- if includeEvidenceAttachments then EvidenceAttachments.fetch doc else return []
#     runJSONGenT $ do
#       J.value "id" $ show $ documentid doc
#       J.value "title" $ documenttitle doc
#       J.value "file" $ fmap fileJSON file
#       J.value "sealedfile" $ fmap fileJSON sealedfile
#       J.value "authorattachments" $ map fileJSON authorattachmentfiles
#       J.objects "evidenceattachments" $ for evidenceattachments $ \a -> do
#         J.value "name"     $ BSC.unpack $ EvidenceAttachments.name a
#         J.value "mimetype" $ BSC.unpack <$> EvidenceAttachments.mimetype a
#         J.value "downloadLink" $ show $ LinkEvidenceAttachment (documentid doc) (EvidenceAttachments.name a)
#       J.value "time" $ jsonDate (Just $ documentmtime doc)
#       J.value "ctime" $ jsonDate (Just $ documentctime doc)
#       J.value "timeouttime" $ jsonDate $ documenttimeouttime doc
#       J.value "autoremindtime" $ jsonDate $ documentautoremindtime doc
#       J.value "status" $ show $ documentstatus doc
#       J.value "state" $ show $ documentstatus doc
#       J.objects "signatories" $ map (signatoryJSON forapi forauthor doc msl) (documentsignatorylinks doc)
#       J.value "signorder" $ unSignOrder $ documentcurrentsignorder doc
#       J.value "authentication" $ case nub (map signatorylinkauthenticationmethod (documentsignatorylinks doc)) of
#                                    [StandardAuthentication] -> "standard"
#                                    [ELegAuthentication]     -> "eleg"
#                                    [SMSPinAuthentication]   -> "sms_pin"
#                                    _                        -> "mixed"
#       J.value "delivery" $ case nub (map signatorylinkdeliverymethod (documentsignatorylinks doc)) of
#                                    [EmailDelivery]   -> "email"
#                                    [PadDelivery]     -> "pad"
#                                    [APIDelivery]     -> "api"
#                                    [MobileDelivery]  -> "mobile"
#                                    [EmailAndMobileDelivery]-> "email_mobile"
#                                    _                 -> "mixed"
#       J.value "template" $ isTemplate doc
#       J.value "daystosign" $ documentdaystosign doc
#       J.value "daystoremind" $ documentdaystoremind doc
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
#         title <- fromJSValueField "title"
#         (invitationmessage :: Maybe (Maybe String)) <-  fromJSValueField "invitationmessage"
#         (confirmationmessage :: Maybe (Maybe String)) <-  fromJSValueField "confirmationmessage"
#         daystosign <- fromJSValueField "daystosign"
#         daystoremind <- fromJSValueField "daystoremind"
#         showheader <- fromJSValueField "showheader"
#         showpdfdownload <- fromJSValueField "showpdfdownload"
#         showrejectoption <- fromJSValueField "showrejectoption"
#         showfooter <- fromJSValueField "showfooter"
#         authentication <-  fromJSValueField "authentication"
#         delivery <-  fromJSValueField "delivery"
#         signatories <-  fromJSValueFieldCustom "signatories" (fromJSValueManyWithUpdate (fromMaybe [] $ documentsignatorylinks <$> mdoc))
#         lang <- fromJSValueField "lang"
#         mtimezone <- fromJSValueField "timezone"
#         doctype <- fmap (\t -> if t then Template else Signable) <$> fromJSValueField "template"
#         tags <- fromJSValueFieldCustom "tags" $ fromJSValueCustomMany  fromJSValue
#         (apicallbackurl :: Maybe (Maybe String)) <- fromJSValueField "apicallbackurl"
#         saved <- fromJSValueField "saved"
#         authorattachments <- fromJSValueFieldCustom "authorattachments" $ fromJSValueCustomMany $ fmap (join . (fmap maybeRead)) $ (fromJSValueField "id")
#         let daystosign'  = min 90 $ max 1 $ updateWithDefaultAndField 14 documentdaystosign daystosign
#         let daystoremind' = min daystosign' <$> max 1 <$> updateWithDefaultAndField Nothing documentdaystoremind daystoremind

#         return $ Just defaultValue {
#             documenttitle = updateWithDefaultAndField "" documenttitle title,
#             documentlang  = updateWithDefaultAndField LANG_SV documentlang lang,
#             documentinvitetext = case (invitationmessage) of
#                                      Nothing -> fromMaybe "" $ documentinvitetext <$> mdoc
#                                      Just Nothing -> ""
#                                      Just (Just s) -> fromMaybe "" (resultToMaybe $ asValidInviteText s),
#             documentconfirmtext = case (confirmationmessage) of
#                                      Nothing -> fromMaybe "" $ documentconfirmtext <$> mdoc
#                                      Just Nothing -> ""
#                                      Just (Just s) -> fromMaybe "" (resultToMaybe $ asValidInviteText s),
#             documentdaystosign   = daystosign',
#             documentdaystoremind = daystoremind',
#             documentshowheader = updateWithDefaultAndField True documentshowheader showheader,
#             documentshowpdfdownload = updateWithDefaultAndField True documentshowpdfdownload showpdfdownload,
#             documentshowrejectoption = updateWithDefaultAndField True documentshowrejectoption showrejectoption,
#             documentshowfooter = updateWithDefaultAndField True documentshowfooter showfooter,
#             documentsignatorylinks = mapAuth authentication $ mapDL delivery $ updateWithDefaultAndField [] documentsignatorylinks signatories,
#             documentauthorattachments = updateWithDefaultAndField [] documentauthorattachments (fmap AuthorAttachment <$> authorattachments),
#             documenttags = updateWithDefaultAndField Set.empty documenttags (Set.fromList <$> tags),
#             documenttype = updateWithDefaultAndField Signable documenttype doctype,
#             documentapicallbackurl = updateWithDefaultAndField Nothing documentapicallbackurl apicallbackurl,
#             documentunsaveddraft = updateWithDefaultAndField False documentunsaveddraft (fmap not saved),
#             documenttimezonename = updateWithDefaultAndField defaultTimeZoneName documenttimezonename (unsafeTimeZoneName <$> mtimezone)
#           }
#       where
#        updateWithDefaultAndField :: a -> (Document -> a) -> Maybe a -> a
#        updateWithDefaultAndField df uf mv = fromMaybe df (mv `mplus` (fmap uf mdoc))
#        mapDL :: Maybe DeliveryMethod -> [SignatoryLink] -> [SignatoryLink]
#        mapDL Nothing sls = sls
#        mapDL (Just dl) sls = map (\sl -> sl {signatorylinkdeliverymethod = dl}) sls
#        mapAuth :: Maybe AuthenticationMethod -> [SignatoryLink] -> [SignatoryLink]
#        mapAuth Nothing sls = sls
#        mapAuth (Just au) sls = map (\sl -> sl {signatorylinkauthenticationmethod = au}) sls
