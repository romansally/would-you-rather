from fastapi import APIRouter

# Create a router to group all poll-related endpoints
router = APIRouter(prefix="/polls", tags=["polls"])

# Simple health check route to confirm the polls router is working
@router.get("/health")
def health():
    return {"ok": True}
