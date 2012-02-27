#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2012, Polar Mobile.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name Polar Mobile nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL POLAR MOBILE BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Used to process the http request.
from itty import post, Response

# Used to validate the values passed into the base url and raise errors.
from publisher.utils import check_base_url, raise_error

# Used to match URLs.
from constants import API, VERSION, FORMAT, PRODUCT_CODE

# Used to validate a session key.
from publisher.model import model

# Used to encode post bodies using json.
from simplejson import dumps


def get_session_id(url, environment):
    '''
    Checks for the existence of the auth-scheme token and then extracts the
    session id and returns it. Note that the auth API entry point has a
    different auth-scheme token.

    Server Errors:

        This section documents errors that are persisted on the server and not
        sent to the client. Note that the publisher is free to modify the
        content of these messages as they please.

        InvalidAuthScheme:

            Returned when the publisher does not recognize the requested
            format.

            Code: InvalidAuthScheme
            Message: Varies with the error.
            HTTP Error Code: 400.
            Required: No
    '''
    # All of the errors in this function share a common code and status.
    code = 'InvalidAuthScheme'
    status = 400

    # Make sure the token is provided.
    if 'HTTP_AUTHORIZATION' not in environment:
        message = 'The authorization token has not been provided.'
        raise_error(url, code, message, status)

    # Make sure the token is provided. The auth-scheme token isn't important
    # for this part of the API, but it is for others.
    token = environment['HTTP_AUTHORIZATION']
    scheme = 'PolarPaywallProxySessionv1.0.0 session:'
    if token.startswith(scheme) == False:
        message = 'The authorization token is incorrect.'
        raise_error(url, code, message, status)

    # Try to extract the session key. The syntax below extracts the characters
    # from the length of the scheme string to the end. Note that whitespace
    # characters are stripped from the session_id.
    session_id = token[len(scheme):].strip()

    # Check to make sure a session id has actually been provided.
    if len(session_id) == 0:
        message = 'The session id has not been provided.'
        raise_error(url, code, message, status)

    # Return the session key.
    return session_id


@post(API + VERSION + FORMAT + r'/validate' + PRODUCT_CODE)
def validate(request, api, version, format, product_code):
    '''
    Overview:

        Attempt an authorization for a product using supplied session key
        (transmitted via the Authorization header). This API call is used
        periodically to validate that the session is still valid and the user
        should continue to be allowed to access protected resources. If the
        call returns a 401, a new authentication call must be made. The base
        URL scheme for this entry point is:

            /:api/:version/:format/validate/:productcode

        In this particular case, the api is "paywallproxy" and the version is
        v1.0.0. Currently, the only supported format is "json". The URL for
        this entry point therefore looks like:

            /paywallproxy/v1.0.0/json/validate/:productcode

        If the product cannot be found, an "InvalidProduct" error should be
        returned. This error will be returned to the client. A full list of
        errors that this entry point returns is available below. Client errors
        are proxied to the client. Server errors remain on Polar's server.

    Parameters:

        There are two sets of parameters that this API entry point requires.
        The first set consists of the product code, which is specified in the
        URL and the session id, which is specified in the authorization header.

        The product code is part of the URL. It is a publisher-assigned unique
        identifier for this product. The product code is required.

        An auth-scheme token is expected when a call is made to this API end
        point. It must conform to RFC 2617 specifications. The authorization
        header has the following form:

            Authorization: PolarPaywallProxySessionv1.0.0 session:<session id>

        Note that the session id is passed as a parameter through the
        authorization token.

        Details regarding the various parameters are described below.

        Product Code:

            A publisher-assigned unique identifier for this product.

            Availability: >= v1.0.0
            Required: Yes
            Location: URL
            Format: URL
            Type: String
            Max Length: 256

        Session Id:

            A session id generated by calling the auth entry point of this
            API.

            Availability: >= v1.0.0
            Required: Yes
            Location: Header
            Format: Header
            Type: String
            Max Length: 512

    Response:

        The following parameters are returned by this API end point. The
        resposne is json encoded. It has two keys; "sessionKey" and "products".
        "sessionKey" is a key that allows the client to re-authenticate without
        the supplied authentication parameters. "products" is a list of product
        identifiers that the user has access to.

        sessionKey:

            A key that allows the client to re-authenticate without the
            supplied authentication parameters.

            Availability: >= v1.0.0
            Required: Yes
            Location: POST Body
            Format: json
            Type: string
            Max Length: 512

        products:

            A list of product identifiers that the user has access to.

            Availability: >= v1.0.0
            Required: Yes
            Location: POST Body
            Format: json
            Type: list
            Max Length: N/A

        product:

            A publisher-assigned unique identifier for this product that the
            user has access to. Contained in the "products" list.

            Availability: >= v1.0.0
            Required: Yes
            Location: POST Body
            Format: json
            Type: string
            Max Length: 256

    Example:

        Example Request:

            POST /validate/gold-level HTTP/1.1
            Authorization: PolarPaywallProxySessionv1.0.0 session:9c4a51cc08d1

        Example Response:

            HTTP/1.1 200 OK
            Content-Type: application/json
            
            {
                "sessionKey": "9c4a51cc08d1",
                
                "products": [
                    "gold-level",
                    "silver-level"
                ]
            }

    Client Errors:

        This section documents errors that are returned to the client. Note
        that the publisher is free to modify the content of these messages as
        they please.

        AccountProblem:

            There is a problem with the user's account. The user is
            prompted to contact technical support.

            Code: InvalidPaywallCredentials
            Message: Your account is not valid. Please contact support.
            HTTP Error Code: 403
            Required: Yes

        InvalidProduct:

            Thrown when the product code indicated is invalid.

            Code: InvalidProduct
            Message: The requested article could not be found.
            HTTP Error Code: 404
            Required: Yes

        SessionExpired:

            The session key provided has expired. Re-authenticate (to obtain
            a new session key) and retry the request.

            Code: SessionExpired
            Message: The session key provided has expired.
            HTTP Error Code: 401
            Required: Yes

    Server Errors:

        This section documents errors that are persisted on the server and not
        sent to the client. Note that the publisher is free to modify the
        content of these messages as they please.

        Some of the following errors are marked optional. They are included in
        this example for completeness and testing purposes. Implementing them
        makes testing the connection between Polar's server and the publishers
        server easier.

        InvalidAPI:

            Returned when the publisher does not recognize the requested api.

            Code: InvalidAPI
            Message: The requested api is not implemented: <api>
            HTTP Error Code: 404
            Required: No

        InvalidVersion:

            Returned when the publisher does not recognize the requested
            version.

            Code: InvalidVersion
            Message: The requested version is not implemented: <version>
            HTTP Error Code: 404
            Required: No

        InvalidFormat:

            Returned when the publisher does not recognize the requested
            format.

            Code: InvalidFormat
            Message: Varies with the error.
            HTTP Error Code: 400.
            Required: No

        InvalidAuthScheme:

            Returned when the publisher does not recognize the requested
            format.

            Code: InvalidAuthScheme
            Message: Varies with the error.
            HTTP Error Code: 400.
            Required: No
    '''
    # Store the full URL string so that it can be used to report errors.
    url = request.path

    # Validate the base URL.
    check_base_url(url, api, version, format)

    # Get the session id from the auth-scheme token.
    session_id = get_session_id(url, request._environ)

    # Check to make sure there is no request body. Any whitespace characters
    # are removed first before the comparison is made.
    if len(request.body.strip()) > 0:
        # If there is a body for this API call, that implies that the caller
        # is not conforming to the API, so raise an error.
        code = 'InvalidFormat'
        message = 'Invalid post body.'
        status = 400
        raise_error(url, code, message, status)

    # Validate the session id.
    data_model = model()
    products = data_model.validate_session(url, session_id)

    # Create the resulting response.
    result = {}
    result['sessionKey'] = session_id
    result['products'] = products

    # Encode the result as a json object.
    content = dumps(result)

    # Extract the authentication token and send it back.
    authorization = request._environ['HTTP_AUTHORIZATION']
    headers = [('Authorization', authorization)]

    # Create and send a response.
    status = 200
    content_type = 'application/json'
    return Response(content, headers, status, content_type)
