from typing import Dict
from typing import Optional

from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.openapi.models import OAuthFlows 
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param


class OAuth2PwdBearer(OAuth2):

    def __init__(
            self,
            tokenUrl: str,
            scheme_name: Optional[str] = None,
            scopes: Optional[Dict[str,str]] = None,
            auto_error: bool = True,
    ):
        
        if not scopes:
            scopes = {}
        
        flows = OAuthFlows(password={"tokenUrl":tokenUrl, "scopes":scopes})
        super().__init__(flows=flows,scheme_name=scheme_name,auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:

        authorization: str = request.cookies.get(
            "access_token"
        )    

        scheme, param = get_authorization_scheme_param(authorization)
        print("Scheme",scheme)
        print("param",param)
        if not authorization or scheme.lower() != 'bearer':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers = {"WWW-Authenticate": "Bearer"}
            )
        else:
            return param
        
        # return param
