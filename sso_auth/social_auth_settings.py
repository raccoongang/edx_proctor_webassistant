# general social auth settings

LOGIN_URL = '/login/sso_pwa-oauth2'
AUTHENTICATION_BACKENDS = (
    'sso_auth.social_auth_backends.PWABackend',
    'django.contrib.auth.backends.ModelBackend',
)
SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'sso_auth.pipeline.create_or_update_permissions',
    'social.pipeline.user.user_details',
    'sso_auth.pipeline.update_user_name'
)

SOCIAL_NEXT_URL = '/'
