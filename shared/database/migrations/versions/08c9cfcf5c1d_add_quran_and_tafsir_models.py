"""add quran and tafsir models

Revision ID: 08c9cfcf5c1d
Revises: a7df729873ae
Create Date: 2026-08-29 14:16:01.158557

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '08c9cfcf5c1d'
down_revision: Union[str, Sequence[str], None] = 'a7df729873ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create quran table
    op.create_table(
        'quran',
        sa.Column('surah_number', sa.Integer(), nullable=False),
        sa.Column('verse_number', sa.Integer(), nullable=False),
        sa.Column('surah_name', sa.String(), nullable=False),
        sa.Column('transliteration', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('verse', sa.String(), nullable=False),
        sa.Column('translation', sa.String(), nullable=False),
        sa.Column('hizb', sa.Integer(), nullable=False),
        sa.Column('hizb_quarter', sa.Integer(), nullable=False),
        sa.Column('page', sa.Integer(), nullable=False),
        sa.Column('ruku', sa.Integer(), nullable=False),
        sa.Column('manzil', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('surah_number', 'verse_number')
    )

    # Create tafsir table
    op.create_table(
        'tafsir',
        sa.Column('surah_number', sa.Integer(), nullable=False),
        sa.Column('verse_number', sa.Integer(), nullable=False),
        sa.Column('commentator', sa.String(), nullable=False),
        sa.Column('text', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['surah_number', 'verse_number'], ['quran.surah_number', 'quran.verse_number'], ),
        sa.PrimaryKeyConstraint('surah_number', 'verse_number', 'commentator')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('tafsir')
    op.drop_table('quran')
