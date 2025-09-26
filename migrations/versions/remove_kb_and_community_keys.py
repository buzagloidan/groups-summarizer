"""Remove KB topics table and community keys from group table

Revision ID: remove_kb_and_community_keys
Revises: bbba88e22126
Create Date: 2025-01-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'remove_kb_and_community_keys'
down_revision: Union[str, None] = 'bbba88e22126'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove community_keys column and its index from group table
    op.drop_index('idx_group_community_keys', table_name='group', if_exists=True)
    op.drop_column('group', 'community_keys')

    # Remove last_ingest column from group table (no longer needed)
    op.drop_column('group', 'last_ingest')

    # Drop the entire kbtopic table if it exists
    op.drop_table('kbtopic', if_exists=True)


def downgrade() -> None:
    # Recreate kbtopic table
    op.create_table('kbtopic',
        sa.Column('id', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column('embedding', postgresql.ARRAY(sa.REAL()), autoincrement=False, nullable=True),
        sa.Column('group_jid', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
        sa.Column('start_time', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.Column('speakers', sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column('summary', sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column('subject', sa.TEXT(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['group_jid'], ['group.group_jid'], name='kbtopic_group_jid_fkey'),
        sa.PrimaryKeyConstraint('id', name='kbtopic_pkey')
    )

    # Add back community_keys column to group table
    op.add_column('group', sa.Column('community_keys', postgresql.ARRAY(sa.VARCHAR()), autoincrement=False, nullable=True))

    # Add back last_ingest column to group table
    op.add_column('group', sa.Column('last_ingest', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False, server_default=sa.text('now()')))

    # Recreate the index
    op.create_index('idx_group_community_keys', 'group', ['community_keys'], unique=False, postgresql_using='gin')