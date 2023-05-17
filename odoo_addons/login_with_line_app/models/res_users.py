# -*- coding: utf-8 -*-

import logging
import requests

from odoo import api, models, fields
from odoo.exceptions import AccessDenied, UserError
from odoo.addons.auth_signup.models.res_users import SignupError

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    client_secret = fields.Char(string='Client Secret')
    callback = fields.Char(string='Callback')

    @api.model
    def _auth_oauth_signin(self, provider, validation, params):
        _logger.info("params: %s", params)
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
            state = params.get('state')
            if (oauth_provider.name) == "LineApp":
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
    def auth_oauth(self, provider, params):
        client_secret = "a512b710507d682c5dd847b7b49bca89"
        callback = "http://manage.jobar.shop/auth_oauth/signin"

        oauth_provider = self.env['auth.oauth.provider'].browse(provider)
        _logger.info("params: %s", params)
        if (oauth_provider.name) != "LineApp":
            line_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            token_line_params = {
                "grant_type": "authorization_code",
                "client_id": oauth_provider.client_id,
                "client_secret": client_secret,
                "code": params.get('code'),
                "redirect_uri": callback
            }

            response_token = requests.post("https://api.line.me/oauth2/v2.1/token", data=token_line_params,
                                           headers=line_headers)
            token_data = response_token.json()
            access_token = token_data.get("access_token")
            id_token = token_data.get("id_token")

            profile_line_params = {
                "id_token": id_token,
                "client_id": oauth_provider.client_id,
            }

            params["access_token"] = access_token
            response_validation = requests.post("https://api.line.me/oauth2/v2.1/verify", data=profile_line_params,
                                                headers=line_headers)
            validation = response_validation.json()
            validation['user_id'] = validation['sub']
            _logger.info("user_id: %s", validation['user_id'])
        else:
            access_token = params.get('access_token')
            validation = self._auth_oauth_validate(provider, access_token)

        if not validation.get('user_id'):
            if validation.get('id'):
                validation['user_id'] = validation['id']
            elif validation.get('username'):
                validation['user_id'] = validation['username']
            elif validation.get('sub'):
                validation['user_id'] = validation['sub']
            else:
                raise AccessDenied()

        login = self._auth_oauth_signin(provider, validation, params)
        if not login:
            raise AccessDenied()

        return (self.env.cr.dbname, login, access_token)
