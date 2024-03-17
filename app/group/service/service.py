from app.group.dto.dto import (
    Group,
    GroupCreate,
    GroupMembershipRequest,
    MemberRequestsView,
    AdminUser,
)
from app.user.dto.dto import UserID
from app.group.repository.repository import GroupRepository
from fastapi import HTTPException
from typing import List, Optional


class GroupService:
    def __init__(self):
        self.group_repository = GroupRepository()

    def create_group(self, group_create: GroupCreate, user_id: int) -> Group:
        group = self.group_repository.create_group(group_create, user_id)
        return group

    def get_user_groups(self, user_id: int) -> List[Group]:
        return self.group_repository.get_user_groups(user_id)

    def delete_group(self, group_id: int, user_id: int):
        role = self.group_repository.get_member_role(group_id, user_id)
        if role == "ADMIN":
            self.group_repository.delete_group(group_id)
        else:
            raise HTTPException(
                status_code=403, detail="Only group admins can delete the group"
            )

    def study_group_join_request(self, user_id: int, group_id: int):
        return self.group_repository.study_group_join_request(user_id, group_id)

    def get_member_requests_by_user(self, user_id: int) -> List[GroupMembershipRequest]:
        return self.group_repository.get_member_requests_by_user(user_id)

    def get_member_requests(
        self, group_id: int, user_id: int
    ) -> List[MemberRequestsView]:
        role = self.group_repository.get_member_role(group_id, user_id)
        if role == "ADMIN":
            return self.group_repository.get_member_requests(group_id)
        else:
            raise HTTPException(
                status_code=403,
                detail="Only group administrators can view member requests.",
            )

    def add_member(self, request_id: int):
        self.group_repository.add_member(request_id)
        return True

    def deny_request(self, request_id: int):
        return self.group_repository.deny_request(request_id)

    def get_all_members(self, group_id: int, current_user_id: int):
        role = self.group_repository.get_member_role(group_id, current_user_id)
        return self.group_repository.get_all_members(group_id, role, current_user_id)

    def group_withdrawal(self, group_id: int, current_user_id: int):
        role = self.group_repository.get_member_role(group_id, current_user_id)
        if role == "ADMIN":
            return HTTPException(
                status_code=403, detail="Group administrators are not allowed to leave."
            )
        return self.group_repository.group_withdrawal(group_id, current_user_id)

    def remove_member(self, admin_user: AdminUser):
        if admin_user.role == "ADMIN":
            return self.group_repository.remove_member(AdminUser)

    def get_all_groups(self, name: Optional[str] = None):
        groups = self.group_repository.get_all_groups(name)
        if not groups:
            raise HTTPException(status_code=404, detail="No groups found")
        return groups

    def change_member_role_to_admin(self, role: str, group_id: int, user_id: int):
        if role == "ADMIN":
            return self.group_repository.change_member_role_to_admin(group_id, user_id)

    def change_member_role_to_member(self, role: str, group_id: int, user_id: int):
        if role == "ADMIN":
            return self.group_repository.change_member_role_to_member(group_id, user_id)
