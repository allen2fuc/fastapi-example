from sqlmodel import SQLModel, Field, ForeignKey, Column, Integer


class UserRole(SQLModel, table=True):
    __tablename__ = "sys_user_roles"

    __table_args__ = {
        "comment": "用户角色表",
    }

    user_id: int = Field(sa_column=Column(Integer, ForeignKey("sys_users.id", ondelete="cascade"), primary_key=True, nullable=False, comment="用户ID"))
    role_id: int = Field(sa_column=Column(Integer, ForeignKey("sys_roles.id", ondelete="cascade"), primary_key=True, nullable=False, comment="角色ID"))


class RoleMenu(SQLModel, table=True):
    __tablename__ = "sys_role_menus"

    __table_args__ = {
        "comment": "角色菜单表",
    }

    role_id: int = Field(sa_column=Column(Integer, ForeignKey("sys_roles.id", ondelete="cascade"), primary_key=True, nullable=False, comment="角色ID"))
    menu_id: int = Field(sa_column=Column(Integer, ForeignKey("sys_menus.id", ondelete="cascade"), primary_key=True, nullable=False, comment="菜单ID"))
