from fastapi import HTTPException, status

class CustomHTTPException:
    @staticmethod
    def unauthorized_exception():
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    @staticmethod
    def not_found_exception(detail: str):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )
