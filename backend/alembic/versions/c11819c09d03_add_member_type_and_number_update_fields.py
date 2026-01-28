"""Add member type and number, update fields

Revision ID: c11819c09d03
Revises: 85cf940e598f
Create Date: 2026-01-28 22:50:50.403051

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c11819c09d03'
down_revision: Union[str, Sequence[str], None] = '85cf940e598f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### Manually adjusted migration to handle existing data ###

    # Step 1: Add the new columns as nullable
    op.add_column('members', sa.Column('member_type', sa.Enum('ADHERENTE', 'DEPORTIVO', 'NA', name='member_type_enum', native_enum=False), nullable=True))
    op.add_column('members', sa.Column('member_number', sa.String(), nullable=True))

    # Step 2: Set a default value for existing rows for the new non-nullable column
    op.execute("UPDATE members SET member_type = 'NA' WHERE member_type IS NULL")

    # Step 3: Alter columns to their final state (NOT NULL or NULL)
    op.alter_column('members', 'member_type', nullable=False)
    op.alter_column('members', 'phone', existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column('members', 'email', existing_type=sa.VARCHAR(), nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### Manually adjusted migration to handle downgrade ###
    op.alter_column('members', 'email', existing_type=sa.VARCHAR(), nullable=False) # Revert to non-nullable based on original user intent
    op.alter_column('members', 'phone', existing_type=sa.VARCHAR(), nullable=True)
    op.drop_column('members', 'member_number')
    op.drop_column('members', 'member_type')
    # ### end Alembic commands ###
