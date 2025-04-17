import httplib2
import os
import random
import sys
import time

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from libs.common import log_or_print

# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 3

# Maximum number of times to retry before giving up.
MAX_RETRIES = 5

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google API Console at
# https://console.cloud.google.com/.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secrets.json"

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the API Console
https://console.cloud.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(
    os.path.join(os.path.dirname(__file__), CLIENT_SECRETS_FILE)
)

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def get_authenticated_service(args):
    flow = flow_from_clientsecrets(
        CLIENT_SECRETS_FILE,
        scope=YOUTUBE_UPLOAD_SCOPE,
        message=MISSING_CLIENT_SECRETS_MESSAGE,
    )

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage, args)

    return build(
        YOUTUBE_API_SERVICE_NAME,
        YOUTUBE_API_VERSION,
        http=credentials.authorize(httplib2.Http()),
    )


def initialize_upload(youtube, options, logger=None):
    tags = None
    if getattr(options, "keywords", None):
        tags = options.keywords.split(",")

    body = dict(
        snippet=dict(
            title=options.title,
            description=options.description,
            tags=tags,
            categoryId=options.category,
        ),
        status=dict(privacyStatus=options.privacyStatus),
    )

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        # The chunksize parameter specifies the size of each chunk of data, in
        # bytes, that will be uploaded at a time. Set a higher value for
        # reliable connections as fewer chunks lead to faster uploads. Set a lower
        # value for better recovery on less reliable connections.
        #
        # Setting "chunksize" equal to -1 in the code below means that the entire
        # file will be uploaded in a single HTTP request. (If the upload fails,
        # it will still be retried where it left off.) This is usually a best
        # practice, but if you're using Python older than 2.6 or if you're
        # running on App Engine, you should set the chunksize to something like
        # 1024 * 1024 (1 megabyte).
        media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True),
    )

    resumable_upload(insert_request, logger=logger)


# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(insert_request, logger=None):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            log_or_print("Uploading file...", logger)
            status, response = insert_request.next_chunk()
            if response is not None:
                if "id" in response:
                    log_or_print(f"Video id '{response['id']}' was successfully uploaded.", logger)
                    # provide the youtube link of the uploaded video
                    video_link = f"https://www.youtube.com/watch?v={response['id']}"
                    log_or_print(f"Video link: {video_link}", logger)
                else:
                    exit(f"The upload failed with an unexpected response: {response}")
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = f"A retriable HTTP error {e.resp.status} occurred:\n{e.content}"
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = f"A retriable error occurred: {e}"

        if error is not None:
            log_or_print(error, logger)
            retry += 1
            if retry > MAX_RETRIES:
                exit("No longer attempting to retry.")

            max_sleep = 2**retry
            sleep_seconds = random.random() * max_sleep
            log_or_print(f"Sleeping {sleep_seconds} seconds and then retrying...", logger)
            time.sleep(sleep_seconds)


def init_oauth_argparser(add_to_parser=None):
    if add_to_parser:
        parser = add_to_parser
    else:
        parser = argparser

    parser.add_argument("--file", help="Video file to upload")
    parser.add_argument("--title", help="Video title")
    parser.add_argument("--description", help="Video description")
    parser.add_argument(
        "--category",
        default="22",
        help="Numeric video category. "
        + "See https://developers.google.com/youtube/v3/docs/videoCategories/list",
    )
    parser.add_argument(
        "--keywords", help="Video keywords, comma separated", default=""
    )
    parser.add_argument(
        "--privacyStatus",
        choices=VALID_PRIVACY_STATUSES,
        default=VALID_PRIVACY_STATUSES[1],
        help="Video privacy status. Default is 'private'",
    )
    if add_to_parser:
        return parser

    args = parser.parse_args()
    args.noauth_local_webserver = True
    return args

def process_oauth_args(args, target_dir=None):
    if target_dir and os.path.isdir(target_dir):
        files = os.listdir(target_dir)
        if not files:
            exit(
                "The specified directory is empty. Please provide a valid file or directory with files."
            )
        args.file = os.path.join(os.path.abspath(target_dir), files[0])

    if not getattr(args, "file", None) or not os.path.exists(args.file):
        exit("Please specify a valid file using the --file= parameter.")

    file_name = os.path.splitext(os.path.basename(args.file))[0]

    # Populate default values for title, description, and other fields
    if getattr(args, "title", None) is None:
        args.title = file_name.strip()
    if getattr(args, "description", None) is None:
        args.description = file_name.strip()

if __name__ == "__main__":
    args = init_oauth_argparser()
    process_oauth_args(args)
    youtube = get_authenticated_service(args)
    try:
        initialize_upload(youtube, args)
    except HttpError as e:
        log_or_print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
    except Exception as e:
        log_or_print(f"An error occurred: {e}")
        