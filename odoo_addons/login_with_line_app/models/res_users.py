# -*- coding: utf-8 -*-

import json
import logging
import requests

from odoo import api, models
from odoo.exceptions import AccessDenied, UserError
from odoo.addons.auth_signup.models.res_users import SignupError

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _auth_oauth_validate(self, provider, access_token):
        """ return the validation data corresponding to the access token """
        oauth_provider = self.env['auth.oauth.provider'].browse(provider)
        validation = self._auth_oauth_rpc(oauth_provider.validation_endpoint, access_token, provider)
        if validation.get("error"):
            raise Exception(validation['error'])
        if oauth_provider.data_endpoint:
            data = self._auth_oauth_rpc(oauth_provider.data_endpoint, access_token)
            validation.update(data)
        return validation

    @api.model
    def _auth_oauth_signin(self, provider, validation, params):
        _logger.info("params" + params)
        oauth_uid = validation['user_id']
        oauth_provider = self.env['auth.oauth.provider'].browse(provider)
        try:
            oauth_user = self.search([("oauth_uid", "=", oauth_uid), ('oauth_provider_id', '=', provider)])
            if not oauth_user:
                raise AccessDenied()
            assert len(oauth_user) == 1
            oauth_user.write({'oauth_access_token': params['access_token']})
            return oauth_user.login
        except AccessDenied as access_denied_exception:
            if self.env.context.get('no_user_creation'):
                return None
            state = json.loads(params['state'])
            if oauth_provider.name.find("Line") != -1:
                token = params.get('access_token')
            else:
                token = state.get('t')
            values = self._generate_signup_values(provider, validation, params)
            try:
                _, login, _ = self.signup(values, token)
                return login
            except (SignupError, UserError):
                raise access_denied_exception

    @api.model
    def _auth_oauth_validate(self, provider, access_token):
        """ return the validation data corresponding to the access token """
        oauth_provider = self.env['auth.oauth.provider'].browse(provider)
        validation = self._auth_oauth_rpc(oauth_provider.validation_endpoint, access_token, provider)
        if validation.get("error"):
            raise Exception(validation['error'])
        if oauth_provider.data_endpoint:
            data = self._auth_oauth_rpc(oauth_provider.data_endpoint, access_token)
            validation.update(data)
        return validation

    @api.model
    def auth_oauth(self, provider, params):

        client_secret = "948f4566998ac5d71f8d3cf733162e80"
        callback = "https://haohaochi.subuy.net/auth_oauth/signin"
        oauth_provider = self.env['auth.oauth.provider'].browse(provider)
        _logger.info("Test by Aaronace")
        _logger.info("params" + params)

        if oauth_provider.name.find("Line") != 5:
            line_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            token_line_params = {
                "grant_type": "authorization_code",
                "client_id": oauth_provider.cliend_id,
                # "client_secret": oauth_provider.client_secret,
                "client_secret": client_secret,
                "code": params.get('code'),
                "redirect_uri": callback
            }

            response_token = requests.post("https://api.line.me/oauth2/v2.1/token", data=token_line_params,
                                           headers=line_headers)
            load = json.loads(response_token.text)

            access_token = load.get("access_token")
            id_token = load.get("id_token")

            profile_line_params = {
                "id_token": id_token,
                "client_id": oauth_provider.cliend_id,
            }

            params["access_token"] = access_token
            validation = requests.post("https://api.line.me/oauth2/v2.1/verify", data=profile_line_params,
                                       headers=line_headers)
            validation = json.loads(validation.text)
            validation['user_id'] = validation['sub']
            _logger.info("user_id" + validation['user_id'])
        else:
            access_token = params.get('access_token')
            validation = self._auth_oauth_validate(provider, access_token)
        # required check
        if not validation.get('user_id'):
            # Workaround: facebook does not send 'user_id' in Open Graph Api
            if validation.get('id'):
                validation['user_id'] = validation['id']
            elif validation.get('username'):
                validation['user_id'] = validation['username']
            elif validation.get('sub'):
                validation['user_id'] = validation['sub']
            else:
                raise AccessDenied()

        # retrieve and sign in user
        login = self._auth_oauth_signin(provider, validation, params)
        if not login:
            raise AccessDenied()
        # return user credentials
        return (self.env.cr.dbname, login, access_token)
