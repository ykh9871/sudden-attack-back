from app.group.dto.dto import (
    Group,
    GroupCreate,
    GroupMembershipRequest,
    MemberRequestsView,
    AllMembers,
    AdminUser,
)
from app.user.dto.dto import UserID
from datetime import datetime
from typing import List, Optional
import sqlite3


class GroupRepository:
    def __init__(self):
        self.conn = sqlite3.connect("sudden-attack.db", check_same_thread=False)
        self.cursor = self.conn.cursor()

    def create_group(self, group_create: GroupCreate, user_id: UserID) -> Group:
        # 새로운 그룹을 데이터베이스에 추가합니다.
        created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # 동일한 이름의 그룹이 이미 존재하는지 확인합니다.
        self.cursor.execute(
            """
            SELECT id
            FROM 'group'
            WHERE name = ?
            """,
            (group_create.name,),
        )
        existing_group = self.cursor.fetchone()

        if existing_group:
            # 이미 존재하는 그룹이라면 에러를 발생시킵니다.
            raise ValueError("A group with the same name already exists.")

        # 그룹이 존재하지 않는다면 새로운 그룹을 추가합니다.
        self.cursor.execute(
            """
            INSERT INTO 'group' (name, description, created_at)
            VALUES (?, ?, ?)
            """,
            (group_create.name, group_create.description, created_at),
        )
        group_id = self.cursor.lastrowid

        # 새로운 그룹이 추가되었는지 확인합니다.
        if group_id is not None:
            # 그룹 멤버를 추가합니다.
            self.cursor.execute(
                """
                INSERT INTO group_member (user_id, group_id, role, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, group_id, "ADMIN", created_at),
            )
            self.conn.commit()

            # 새로운 그룹을 반환합니다.
            return Group(
                id=group_id,
                name=group_create.name,
                description=group_create.description,
                created_at=created_at,
            )
        else:
            # 그룹 추가에 실패한 경우에 대한 처리
            raise ValueError("Failed to create group")

    def get_user_groups(self, user_id: UserID) -> List[Group]:
        self.cursor.execute(
            """
            SELECT g.id, g.name, g.description, g.created_at
            FROM group_member gm
            JOIN 'group' g ON gm.group_id = g.id
            WHERE gm.user_id = ?
            """,
            (user_id,),
        )
        user_groups = self.cursor.fetchall()
        groups = []
        for group in user_groups:
            groups.append(
                Group(
                    id=group[0],
                    name=group[1],
                    description=group[2],
                    created_at=group[3],
                )
            )
        return groups

    def get_member_role(self, group_id: int, user_id: UserID) -> str:
        self.cursor.execute(
            """
            SELECT role
            FROM group_member
            WHERE group_id = ? 
                AND user_id = ?
            """,
            (group_id, user_id),
        )
        role = self.cursor.fetchone()
        if role:
            return role[0]
        else:
            return None

    def delete_group(self, group_id: int):
        # 외래 키 제약 조건 활성화
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        self.cursor.execute(
            """
            DELETE
            FROM 'group'
            WHERE id = ?
            """,
            (group_id,),
        )
        self.conn.commit()

    def study_group_join_request(self, user_id: UserID, group_id: int):
        created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            """
            INSERT INTO group_member (user_id, group_id, created_at)
            VALUES (?, ?, ?)
            """,
            (user_id, group_id, created_at),
        )
        self.conn.commit()
        return {"message": "Group membership request created successfully"}

    def get_member_requests_by_user(
        self, user_id: UserID
    ) -> List[GroupMembershipRequest]:
        self.cursor.execute(
            """
            SELECT g.name, gm.created_at
            FROM group_member gm
            JOIN 'group' g ON gm.group_id = g.id
            WHERE gm.user_id = ? 
                AND gm.role = 'PENDING'
            """,
            (user_id,),
        )
        rows = self.cursor.fetchall()
        requests = []
        for row in rows:
            requests.append(
                GroupMembershipRequest(group_name=row[0], created_at=row[1])
            )
        return requests

    def get_member_requests(self, group_id: int) -> List[MemberRequestsView]:
        self.cursor.execute(
            """
            SELECT gm.id, u.username, u.nickname, o.occupation_name, gm.created_at
            FROM group_member gm
            JOIN user u ON gm.user_id = u.id
            JOIN occupation o ON u.occupation_id = o.id
            WHERE gm.group_id = ? 
                AND gm.role = 'PENDING'
            """,
            (group_id,),
        )
        rows = self.cursor.fetchall()
        requests = []
        for row in rows:
            requests.append(
                MemberRequestsView(
                    id=row[0],
                    username=row[1],
                    nickname=row[2],
                    occupation_name=row[3],
                    created_at=row[4],
                )
            )
        return requests

    def deny_request(self, request_id: int):
        self.cursor.execute(
            """
            DELETE
            FROM group_member
            WHERE id = ?
            """,
            (request_id,),
        )
        self.conn.commit()
        return self.cursor.rowcount

    def add_member(self, request_id: int):
        self.cursor.execute(
            """
            UPDATE group_member
            SET role=?, created_at=?
            WHERE id=?
            """,
            ("MEMBER", datetime.now().strftime("%Y-%m-%d %H:%M"), request_id),
        )
        self.conn.commit()

    def get_all_members(self, group_id: int, role: str, current_user_id: int):
        self.cursor.execute(
            """
            SELECT gm.user_id, u.nickname, gm.role
            FROM group_member gm
            JOIN user u ON gm.user_id = u.id
            WHERE gm.group_id = ? 
                AND gm.role != 'PENDING'
            """,
            (group_id,),
        )
        members = self.cursor.fetchall()
        members_info = []
        for member in members:
            members_info.append(
                AllMembers(
                    id=member[0],
                    nickname=member[1],
                )
            )
        return current_user_id, role, members

    def group_withdrawal(self, group_id: int, current_user_id: UserID):
        self.cursor.execute(
            """
            DELETE
            FROM group_member
            WHERE user_id = ? 
                AND group_id = ?
            """,
            (current_user_id, group_id),
        )
        self.conn.commit()
        return {"message": "Successfully left the group."}

    def remove_member(self, admin_user: AdminUser):
        self.cursor.execute(
            """
            DELETE
            FROM group_member
            WHERE user_id = ? 
                AND group_id = ?
            """,
            (admin_user.user_id, admin_user.group_id),
        )
        self.conn.commit()
        return {"message": "Successfully removed a member."}

    def get_all_groups(self, name: Optional[str] = None):
        if name:
            self.cursor.execute(
                """
                SELECT g.id, g.name, g.description, g.created_at, COUNT(gm.group_id) AS member_count
                FROM 'group' g
                LEFT JOIN group_member gm ON gm.group_id = g.id 
                    AND gm.role != 'PENDING'
                WHERE g.name LIKE ?
                GROUP BY g.id
                """,
                ("%" + name + "%",),
            )
        else:
            self.cursor.execute(
                """
                SELECT g.id, g.name, g.description, g.created_at, COUNT(gm.group_id) AS member_count
                FROM 'group' g
                LEFT JOIN group_member gm ON gm.group_id = g.id 
                    AND gm.role != 'PENDING'
                GROUP BY g.id
                """
            )
        # 결과를 파이썬 객체로 변환하여 반환
        groups = []
        for row in self.cursor.fetchall():
            group = {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "created_at": row[3],
                "member_count": row[4],
            }
            groups.append(group)
        return groups

    def change_member_role_to_admin(self, group_id: int, user_id: int):
        if self.get_member_role(group_id, user_id) == "ADMIN":
            return {"message": "User's role is already ADMIN"}

        self.cursor.execute(
            """
            UPDATE group_member
            SET role=?
            WHERE group_id = ? 
                AND user_id = ?
            """,
            ("ADMIN", group_id, user_id),
        )
        self.conn.commit()
        return {"message": "Successfully changed."}

    def change_member_role_to_member(self, group_id: int, user_id: int):
        if self.get_member_role(group_id, user_id) == "MEMBER":
            return {"message": "User's role is already MEMBER"}

        self.cursor.execute(
            """
            UPDATE group_member
            SET role=?
            WHERE group_id = ? 
                AND user_id = ?
            """,
            ("MEMBER", group_id, user_id),
        )
        self.conn.commit()
        return {"message": "Successfully changed."}
