"""add product description

Revision ID: 20260510_0002
Revises: 20260510_0001
Create Date: 2026-05-10 00:02:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260510_0002"
down_revision: Union[str, None] = "20260510_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("products") as batch_op:
        batch_op.add_column(
            sa.Column(
                "description",
                sa.String(length=500),
                nullable=False,
                server_default="No description",
            )
        )
    with op.batch_alter_table("products") as batch_op:
        batch_op.alter_column("description", server_default=None)


def downgrade() -> None:
    with op.batch_alter_table("products") as batch_op:
        batch_op.drop_column("description")
