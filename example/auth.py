from connexion.exceptions import OAuthProblem


X_API_KEY = "some-string"

def apikey_auth(token, required_scopes):
    if X_API_KEY != token:
        raise OAuthProblem('Invalid token')
    return {}
