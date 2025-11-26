"""
Custom JWT Authentication that checks blacklist.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken


class BlacklistJWTAuthentication(JWTAuthentication):
    """JWT Authentication that checks blacklist."""
    
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        
        # Check if token is blacklisted
        jti = validated_token.get('jti')
        if jti:
            try:
                outstanding_token = OutstandingToken.objects.filter(jti=jti).first()
                if outstanding_token:
                    blacklisted = BlacklistedToken.objects.filter(token=outstanding_token).exists()
                    if blacklisted:
                        from rest_framework_simplejwt.exceptions import TokenError
                        raise TokenError('Token is blacklisted')
            except Exception:
                pass
        
        return self.get_user(validated_token), validated_token

