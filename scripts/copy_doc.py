#!/usr/bin/env python
from scrivepy import FieldPlacement, Signatory, SignatureField, Scrive
import argparse


def clone_placement(fp):
    result = FieldPlacement(left=fp.left, top=fp.top, width=fp.width,
                            height=fp.height, font_size=fp.font_size,
                            page=fp.page, tip=fp.tip)

    return result


def clone_field(f):
    sbfbs = f.should_be_filled_by_sender
    if isinstance(f, SignatureField):
        sbfbs = f.should_be_filled_by_sender
        result = SignatureField(name=f.name, obligatory=f.obligatory,
                                should_be_filled_by_sender=sbfbs)
        result._value = f.value
    else:
        result = type(f)(name=f.name,
                         value=f.value,
                         obligatory=f.obligatory,
                         should_be_filled_by_sender=sbfbs)

    for fp in f.placements:
        result.placements.add(clone_placement(fp))

    return result


def clone_signatory(sl):
    result = Signatory()

    result.sign_order = sl.sign_order
    result.invitation_delivery_method = sl.invitation_delivery_method
    result.confirmation_delivery_method = sl.confirmation_delivery_method
    result.authentication_method = sl.authentication_method
    result.viewer = sl.viewer
    result._author = sl.author
    result.sign_success_redirect_url = sl.sign_success_redirect_url
    result.rejection_redirect_url = sl.rejection_redirect_url

    for f in sl.fields:
        result.fields.add(clone_field(f))

    return result


def copy_doc(d1, d2):
    if d1.original_file is not None:
        file_path = '/tmp/' + d1.original_file.name
        d1.original_file.save_as(file_path)
        d2 = d2._api.change_document_file(d2, file_path)

    d2.title = d1.title
    d2.is_template = d1.is_template
    d2.timezone = d1.timezone
    d2.language = d1.language
    d2.number_of_days_to_sign = d1.number_of_days_to_sign
    d2.show_header = d1.show_header
    d2.show_pdf_download = d1.show_pdf_download
    d2.show_reject_option = d1.show_reject_option
    d2.show_footer = d1.show_footer

    d2.signatories.clear()
    for sl in d1.signatories:
        d2.signatories.add(clone_signatory(sl))

    d2._api.update_document(d2)


if __name__ == '__main__':
    descr = 'Copy documents between servers/accounts'
    parser = argparse.ArgumentParser(description=descr)
    msg = 'Client credentials identifier for source account'
    parser.add_argument('--source-client-credentials-identifier',
                        metavar='ID', type=str, help=msg, required=True)
    msg = 'Client credentials secret for source account'
    parser.add_argument('--source-client-credentials-secret',
                        metavar='ID', type=str, help=msg, required=True)
    msg = 'Token credentials identifier for source account'
    parser.add_argument('--source-token-credentials-identifier',
                        metavar='ID', type=str, help=msg, required=True)
    msg = 'Token credentials secret for source account'
    parser.add_argument('--source-token-credentials-secret',
                        metavar='ID', type=str, help=msg, required=True)
    msg = 'Hostname of source account (e.g. api-testbed.scrive.com)'
    parser.add_argument('--source-hostname',
                        metavar='DOMAIN', type=str, help=msg, required=True)
    msg = 'Source hostname is not using HTTPS'
    parser.add_argument('--source-no-https', help=msg,
                        action='store_true', default=False)
    msg = 'Client credentials identifier for target account'
    parser.add_argument('--target-client-credentials-identifier',
                        metavar='ID', type=str, help=msg, required=True)
    msg = 'Client credentials secret for target account'
    parser.add_argument('--target-client-credentials-secret',
                        metavar='ID', type=str, help=msg, required=True)
    msg = 'Token credentials identifier for target account'
    parser.add_argument('--target-token-credentials-identifier',
                        metavar='ID', type=str, help=msg, required=True)
    msg = 'Token credentials secret for target account'
    parser.add_argument('--target-token-credentials-secret',
                        metavar='ID', type=str, help=msg, required=True)
    msg = 'Hostname of target account (e.g. api-testbed.scrive.com)'
    parser.add_argument('--target-hostname',
                        metavar='DOMAIN', type=str, help=msg, required=True)
    msg = 'Target hostname is not using HTTPS'
    parser.add_argument('--target-no-https', help=msg,
                        action='store_true', default=False)

    msg = 'Ids of the document to copy from source account to target account'
    parser.add_argument('DOCUMENT_ID', type=str, help=msg, nargs='+')

    args = parser.parse_args()

    source_api = Scrive(client_credentials_identifier=
                        args.source_client_credentials_identifier,
                        client_credentials_secret=
                        args.source_client_credentials_secret,
                        token_credentials_identifier=
                        args.source_token_credentials_identifier,
                        token_credentials_secret=
                        args.source_token_credentials_secret,
                        api_hostname=args.source_hostname,
                        https=not args.source_no_https)
    target_api = Scrive(client_credentials_identifier=
                        args.target_client_credentials_identifier,
                        client_credentials_secret=
                        args.target_client_credentials_secret,
                        token_credentials_identifier=
                        args.target_token_credentials_identifier,
                        token_credentials_secret=
                        args.target_token_credentials_secret,
                        api_hostname=args.target_hostname,
                        https=not args.target_no_https)

    for did in args.DOCUMENT_ID:
        source_doc = source_api.get_document(did)
        target_doc = target_api.create_document_from_file(file_path=None)
        copy_doc(source_doc, target_doc)
        print source_doc.id, '->', target_doc.id
