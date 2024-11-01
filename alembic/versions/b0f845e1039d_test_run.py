"""Test run

Revision ID: b0f845e1039d
Revises: 6334a4fb866c
Create Date: 2024-11-01 23:48:39.687355

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b0f845e1039d'
down_revision: Union[str, None] = '6334a4fb866c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
