# app/controllers/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status, Depends, Query
from ..database import get_db
from ..services.auth import AuthService
from ..services.websocket_manager import websocket_manager
from sqlalchemy.orm import Session

router = APIRouter()

@router.websocket("/ws/random-numbers")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),  # Get token from query parameters
    db: Session = Depends(get_db)
):
    print("Trying to initiate WebSocket connection")
    try:
        await websocket.accept()
        
        # Verify the token exists
        if not token:
            print("No token provided in query parameters")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Authenticate user using the token
        user_session = AuthService.get_session(db, token)
        if not user_session:
            print("Authentication failed - invalid token")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        print(f"Authentication successful for user ID: {user_session.user_id}")
        await websocket_manager.connect(websocket, str(user_session.user_id))
        await websocket_manager.stream_numbers(websocket, str(user_session.user_id), db)
            
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for user ID: {user_session.user_id}")
        websocket_manager.disconnect(str(user_session.user_id))
    except Exception as e:
        print(f"Error in WebSocket connection: {str(e)}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)