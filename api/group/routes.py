from fastapi import APIRouter, Depends, HTTPException
from app.user.dto.dto import UserID
from app.group.dto.dto import (
    Group,
    GroupCreate,
    GroupMembershipRequest,
    MemberRequestsView,
    AdminUser,
)
from app.user.service.service import UserService
from app.group.service.service import GroupService
from typing import List, Optional

router = APIRouter()
user_service = UserService()
group_service = GroupService()


@router.post("/group/", response_model=GroupCreate)
async def create_group(
    group_create: GroupCreate,
    user_id: UserID = Depends(user_service.get_userid_by_email),
):
    group = group_service.create_group(group_create, user_id)
    return group


@router.get("/mygroup/", response_model=List[Group])
async def get_user_groups(user_id: UserID = Depends(user_service.get_userid_by_email)):
    user_groups = group_service.get_user_groups(user_id)
    if not user_groups:
        raise HTTPException(status_code=404, detail="User has no groups")
    return user_groups


@router.delete("/mygroup/")
async def delete_group(
    group_id: int, user_id: UserID = Depends(user_service.get_userid_by_email)
):
    try:
        group_service.delete_group(group_id, user_id)
        return {"message": "Group deleted successfully"}
    except HTTPException as e:
        return e


@router.post("/member_requests/")
async def study_group_join_request(
    group_id: int, user_id: UserID = Depends(user_service.get_userid_by_email)
):
    group_service.study_group_join_request(user_id, group_id)
    return {"message": "Successfully send study group join request"}


@router.get("/member_requests/{user_id}", response_model=List[GroupMembershipRequest])
async def get_member_requests_by_user(
    user_id: UserID = Depends(user_service.get_userid_by_email),
):
    requests = group_service.get_member_requests_by_user(user_id)
    if not requests:
        raise HTTPException(status_code=404, detail="No member requests found")
    return requests


@router.get("/member_requests/", response_model=List[MemberRequestsView])
async def get_member_requests(
    group_id: int, user_id: UserID = Depends(user_service.get_userid_by_email)
):
    requests = group_service.get_member_requests(group_id, user_id)
    if not requests:
        raise HTTPException(status_code=404, detail="No member requests found")
    return requests


@router.put("/member_requests/")
async def add_member(request_id: int):
    success = group_service.add_member(request_id)
    if success:
        return {"message": "Successfully added members"}
    else:
        raise HTTPException(status_code=404, detail="Member request not found")


@router.delete("/member_requests/deny_request/")
async def deny_request(request_id: int):
    success = group_service.deny_request(request_id)
    if success == 1:
        return {"message": "Successfully denied request"}
    else:
        raise HTTPException(status_code=404, detail="That's not the right approach.")


@router.get("/group/members")
async def get_all_members(
    group_id: int, current_user_id: UserID = Depends(user_service.get_userid_by_email)
):
    return group_service.get_all_members(group_id, current_user_id)


@router.delete("/group/group_withdrawal")
async def group_withdrawal(
    group_id: int, current_user_id: UserID = Depends(user_service.get_userid_by_email)
):
    return group_service.group_withdrawal(group_id, current_user_id)


@router.delete("/group/remove_member")
async def remove_member(admin_user: AdminUser):
    return group_service.remove_member(admin_user)


@router.get("/group/", response_model=List[Group])
async def get_all_groups(name: Optional[str] = None):
    return group_service.get_all_groups(name)


@router.put("/group/{group_id}/{user_id}/ad")
async def change_member_role_to_admin(role: str, group_id: int, user_id: int):
    return group_service.change_member_role_to_admin(role, group_id, user_id)


@router.put("/group/{group_id}/{user_id}/mem")
async def change_member_role_to_member(role: str, group_id: int, user_id: int):
    return group_service.change_member_role_to_member(role, group_id, user_id)
