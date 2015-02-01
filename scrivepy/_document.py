import enum
from dateutil import parser as dateparser

import type_value_unifier as tvu
from scrivepy import _object, _signatory, _exceptions, _set, _file


scrive_property = _object.scrive_property


class DocumentStatus(unicode, enum.Enum):
    preparation = u'Preparation'
    pending = u'Pending'
    closed = u'Closed'
    canceled = u'Canceled'
    timedout = u'Timedout'
    rejected = u'Rejected'
    error = u'DocumentError'


MaybeUnicode = tvu.nullable(tvu.instance(unicode))


class Language(unicode, enum.Enum):
    english = u'en'
    swedish = u'sv'
    german = u'de'
    french = u'fr'
    italian = u'it'
    spanish = u'es'
    portuguese = u'pt'
    dutch = u'nl'
    danish = u'da'
    norwegian = u'no'
    greek = u'el'
    finnish = u'fi'


class DeletionStatus(enum.Enum):
    not_deleted = 0
    in_trash = 1
    deleted = 2


class Document(_object.ScriveObject):

    @tvu.validate_and_unify(title=tvu.instance(unicode),
                            number_of_days_to_sign=tvu.bounded_int(1, 90),
                            number_of_days_to_remind=
                            tvu.nullable(tvu.PositiveInt),
                            is_template=tvu.instance(bool),
                            show_header=tvu.instance(bool),
                            show_pdf_download=tvu.instance(bool),
                            show_reject_option=tvu.instance(bool),
                            show_footer=tvu.instance(bool),
                            invitation_message=MaybeUnicode,
                            confirmation_message=MaybeUnicode,
                            api_callback_url=MaybeUnicode,
                            language=tvu.instance(Language, enum=True),
                            tags=tvu.UnicodeDict,
                            saved_as_draft=tvu.instance(bool),
                            timezone=tvu.instance(unicode))
    def __init__(self, title=u'', number_of_days_to_sign=14,
                 number_of_days_to_remind=None,
                 show_header=True, show_pdf_download=True,
                 show_reject_option=True, show_footer=True,
                 invitation_message=None, confirmation_message=None,
                 api_callback_url=None, language=Language.swedish,
                 tags={}, is_template=False, saved_as_draft=False,
                 timezone=u'Europe/Stockholm'):
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
        self._show_header = show_header
        self._show_pdf_download = show_pdf_download
        self._show_reject_option = show_reject_option
        self._show_footer = show_footer
        self.invitation_message = invitation_message  # setter has better logic
        self.confirmation_message = \
            confirmation_message  # setter has better logic
        self._api_callback_url = api_callback_url
        self._language = language
        self._tags = tags.copy()
        self._saved_as_draft = saved_as_draft
        self._deletion_status = DeletionStatus.not_deleted
        self._signing_possible = None
        self._object_version = None
        self._timezone = timezone
        self._viewed_by_author = None
        self._access_token = None
        self._signatories = _set.ScriveSet()
        self._signatories._elem_validator = tvu.instance(_signatory.Signatory)
        self._original_file = None

    @classmethod
    def _from_json_obj(cls, json):
        try:
            signatories = [_signatory.Signatory._from_json_obj(signatory_json)
                           for signatory_json in json[u'signatories']]
            lang_code = json[u'lang']
            if lang_code == u'gb':
                lang_code = u'en'
            document = Document(title=json[u'title'],
                                number_of_days_to_sign=json[u'daystosign'],
                                number_of_days_to_remind=json[u'daystoremind'],
                                is_template=json[u'template'],
                                show_header=json[u'showheader'],
                                show_pdf_download=json[u'showpdfdownload'],
                                show_reject_option=json[u'showrejectoption'],
                                show_footer=json[u'showfooter'],
                                invitation_message=json[u'invitationmessage'],
                                confirmation_message=
                                json[u'confirmationmessage'],
                                api_callback_url=json[u'apicallbackurl'],
                                language=Language(lang_code),
                                tags={elem[u'name']: elem[u'value']
                                      for elem in json[u'tags']},
                                saved_as_draft=json[u'saved'],
                                timezone=json[u'timezone'])
            document.signatories.update(signatories)
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
            deleted = json[u'deleted']
            really_deleted = json[u'reallydeleted']
            if deleted and really_deleted:
                document._deletion_status = DeletionStatus.deleted
            elif deleted:
                document._deletion_status = DeletionStatus.in_trash
            document._signing_possible = json[u'canperformsigning']
            document._object_version = json[u'objectversion']
            document._viewed_by_author = json[u'isviewedbyauthor']
            document._access_token = json[u'accesstoken']
            file_json = json.get(u'file')
            if file_json is not None:
                file_ = _file.ScriveFile(id_=file_json[u'id'],
                                         name=file_json[u'name'],
                                         document=document)
                document._original_file = file_

            if document.status is not DocumentStatus.preparation:
                document._set_read_only()

            return document
        except (KeyError, TypeError, ValueError) as e:
            raise _exceptions.InvalidResponse(e)

    def _set_invalid(self):
        # invalidate signatories first, before getter stops working
        self.signatories._set_invalid()
        super(Document, self)._set_invalid()

    def _set_read_only(self):
        super(Document, self)._set_read_only()
        self.signatories._set_read_only()

    def _to_json_obj(self):
        return {u'title': self.title,
                u'daystosign': self.number_of_days_to_sign,
                u'daystoremind': self.number_of_days_to_remind,
                u'template': self.is_template,
                u'showheader': self.show_header,
                u'showpdfdownload': self.show_pdf_download,
                u'showrejectoption': self.show_reject_option,
                u'showfooter': self.show_footer,
                u'invitationmessage': self.invitation_message or u'',
                u'confirmationmessage': self.confirmation_message or u'',
                u'apicallbackurl': self.api_callback_url,
                u'lang': self.language.value,
                u'tags': [{u'name': key, u'value': val}
                          for key, val in self.tags.items()],
                u'saved': self.saved_as_draft,
                u'timezone': self.timezone,
                u'signatories': list(self.signatories)}

    @scrive_property
    def signatories(self):
        return self._signatories

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

    @scrive_property
    def show_header(self):
        return self._show_header

    @show_header.setter
    @tvu.validate_and_unify(show_header=tvu.instance(bool))
    def show_header(self, show_header):
        self._show_header = show_header

    @scrive_property
    def show_pdf_download(self):
        return self._show_pdf_download

    @show_pdf_download.setter
    @tvu.validate_and_unify(show_pdf_download=tvu.instance(bool))
    def show_pdf_download(self, show_pdf_download):
        self._show_pdf_download = show_pdf_download

    @scrive_property
    def show_reject_option(self):
        return self._show_reject_option

    @show_reject_option.setter
    @tvu.validate_and_unify(show_reject_option=tvu.instance(bool))
    def show_reject_option(self, show_reject_option):
        self._show_reject_option = show_reject_option

    @scrive_property
    def show_footer(self):
        return self._show_footer

    @show_footer.setter
    @tvu.validate_and_unify(show_footer=tvu.instance(bool))
    def show_footer(self, show_footer):
        self._show_footer = show_footer

    @scrive_property
    def invitation_message(self):
        return self._invitation_message

    @invitation_message.setter
    @tvu.validate_and_unify(invitation_message=MaybeUnicode)
    def invitation_message(self, invitation_message):
        if invitation_message is not None and invitation_message.isspace()\
           or invitation_message == u'':
            invitation_message = None
        self._invitation_message = invitation_message

    @scrive_property
    def confirmation_message(self):
        return self._confirmation_message

    @confirmation_message.setter
    @tvu.validate_and_unify(confirmation_message=MaybeUnicode)
    def confirmation_message(self, confirmation_message):
        if confirmation_message is not None and confirmation_message.isspace()\
           or confirmation_message == u'':
            confirmation_message = None
        self._confirmation_message = confirmation_message

    @scrive_property
    def api_callback_url(self):
        return self._api_callback_url

    @api_callback_url.setter
    @tvu.validate_and_unify(api_callback_url=MaybeUnicode)
    def api_callback_url(self, api_callback_url):
        self._api_callback_url = api_callback_url

    @scrive_property
    def language(self):
        return self._language

    @language.setter
    @tvu.validate_and_unify(language=tvu.instance(Language, enum=True))
    def language(self, language):
        self._language = language

    @scrive_property
    def tags(self):
        return self._tags

    @tags.setter
    @tvu.validate_and_unify(tags=tvu.UnicodeDict)
    def tags(self, tags):
        self._tags = tags

    @scrive_property
    def saved_as_draft(self):
        return self._saved_as_draft

    @saved_as_draft.setter
    @tvu.validate_and_unify(saved_as_draft=tvu.instance(bool))
    def saved_as_draft(self, saved_as_draft):
        self._saved_as_draft = saved_as_draft

    @scrive_property
    def deletion_status(self):
        return self._deletion_status

    @scrive_property
    def signing_possible(self):
        return self._signing_possible

    @scrive_property
    def object_version(self):
        return self._object_version

    @scrive_property
    def timezone(self):
        return self._timezone

    @timezone.setter
    @tvu.validate_and_unify(timezone=tvu.instance(unicode))
    def timezone(self, timezone):
        self._timezone = timezone

    @scrive_property
    def viewed_by_author(self):
        return self._viewed_by_author

    @scrive_property
    def access_token(self):
        return self._access_token

    @scrive_property
    def original_file(self):
        return self._original_file

    def _set_api(self, api):
        super(Document, self)._set_api(api)
        if self._original_file is not None:
            self._original_file._set_api(api)

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

# instance FromJSValueWithUpdate Document where
#     fromJSValueWithUpdate mdoc = do
#         authorattachments <- fromJSValueFieldCustom "authorattachments" $ fromJSValueCustomMany $ fmap (join . (fmap maybeRead)) $ (fromJSValueField "id")
#         return $ Just defaultValue {
#             documentauthorattachments = updateWithDefaultAndField [] documentauthorattachments (fmap AuthorAttachment <$> authorattachments),
#           }
