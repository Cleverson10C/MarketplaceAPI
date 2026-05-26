"""add rastreamentos produto

Revision ID: 20260525_0002
Revises: 20260523_0001
Create Date: 2026-05-25 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260525_0002"
down_revision: Union[str, None] = "20260523_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rastreamentos_produto",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("produto_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("localizacao", sa.String(), nullable=False),
        sa.Column("observacao", sa.String(), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["produto_id"], ["produtos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_rastreamentos_produto_id"), "rastreamentos_produto", ["id"], unique=False)
    op.create_index(op.f("ix_rastreamentos_produto_produto_id"), "rastreamentos_produto", ["produto_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_rastreamentos_produto_produto_id"), table_name="rastreamentos_produto")
    op.drop_index(op.f("ix_rastreamentos_produto_id"), table_name="rastreamentos_produto")
    op.drop_table("rastreamentos_produto")
