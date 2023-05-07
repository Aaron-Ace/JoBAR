# -*- coding: utf-8 -*-
{
    'name': 'Login With Line Chat App',
    'version': '13.0',
    'sequence': 1,
    'category': 'Authentication',
    'summary': "Login With Line Chat App account",
    'description': "You can now login using your line chat app account.",
    'depends': ['auth_oauth',],
    'data': [
        'data/auth_oauth_data_line.xml',
        'views/auth_oauth_assets.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
