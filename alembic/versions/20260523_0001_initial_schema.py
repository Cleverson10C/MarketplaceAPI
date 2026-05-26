"""initial schema

Revision ID: 20260523_0001
Revises:
Create Date: 2026-05-23 12:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260523_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "produtos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(), nullable=False),
        sa.Column("preco", sa.Float(), nullable=False),
        sa.Column("estoque", sa.Integer(), nullable=False),
        sa.Column("estoque_minimo", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_produtos_id"), "produtos", ["id"], unique=False)

    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("senha", sa.String(), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_usuarios_email"), "usuarios", ["email"], unique=True)
    op.create_index(op.f("ix_usuarios_id"), "usuarios", ["id"], unique=False)

    op.create_table(
        "pedidos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column("total", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pedidos_id"), "pedidos", ["id"], unique=False)

    op.create_table(
        "itens_pedido",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pedido_id", sa.Integer(), nullable=True),
        sa.Column("produto_id", sa.Integer(), nullable=True),
        sa.Column("quantidade", sa.Integer(), nullable=True),
        sa.Column("preco", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["pedido_id"], ["pedidos.id"]),
        sa.ForeignKeyConstraint(["produto_id"], ["produtos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_itens_pedido_id"), "itens_pedido", ["id"], unique=False)

    op.create_table(
        "movimentos_estoque",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("produto_id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(), nullable=False),
        sa.Column("quantidade", sa.Integer(), nullable=False),
        sa.Column("estoque_antes", sa.Integer(), nullable=False),
        sa.Column("estoque_depois", sa.Integer(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["produto_id"], ["produtos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_movimentos_estoque_id"), "movimentos_estoque", ["id"], unique=False)
    op.create_index(op.f("ix_movimentos_estoque_produto_id"), "movimentos_estoque", ["produto_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_movimentos_estoque_produto_id"), table_name="movimentos_estoque")
    op.drop_index(op.f("ix_movimentos_estoque_id"), table_name="movimentos_estoque")
    op.drop_table("movimentos_estoque")
    op.drop_index(op.f("ix_itens_pedido_id"), table_name="itens_pedido")
    op.drop_table("itens_pedido")
    op.drop_index(op.f("ix_pedidos_id"), table_name="pedidos")
    op.drop_table("pedidos")
    op.drop_index(op.f("ix_usuarios_id"), table_name="usuarios")
    op.drop_index(op.f("ix_usuarios_email"), table_name="usuarios")
    op.drop_table("usuarios")
    op.drop_index(op.f("ix_produtos_id"), table_name="produtos")
    op.drop_table("produtos")
