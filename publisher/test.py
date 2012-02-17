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

# Used to define and run unit tests.
from unittest import TestCase, main

# Used to mimic functions like datetime to make testing predictable.
from mock import patch, MagicMock

# Used to test error handling code.
from error import create_error


class TestErrors(TestCase):
    '''
    Test the code in errors.py.
    '''
    def test_create_error(self):
        '''
        Tests generation of an error using positive example.
        '''
        # Generate the example.
        code = 'TestError'
        message = 'This is a test error.'
        resource = '/test'

        # Call create_error and get the result.
        result = create_error(code, message, resource)

        # Check the result's type.
        self.assertIsInstance(result, str)

        # Check the result's content.
        expected = '{"error": {"message": "This is a test error.", '\
            '"code": "TestError", "resource": "/test"}}'
        self.assertEqual(result, expected)

# If the script is called directly, then the global variable __name__ will
# be set to main.
if __name__ == '__main__':
    # Run unit tests if the script is called directly.
    main()