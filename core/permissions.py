from fastapi import Depends, HTTPException, status

from core.auth import get_current_user

def require_roles(*roles):

    def dependency(
        current_user = Depends(get_current_user)
    ):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não possui permissão para realizar esta ação."
            )

        return current_user

    return dependency