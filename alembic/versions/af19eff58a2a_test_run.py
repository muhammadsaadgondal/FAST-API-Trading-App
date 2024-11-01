"""Test run

Revision ID: af19eff58a2a
Revises: b0f845e1039d
Create Date: 2024-11-01 23:49:53.941326

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af19eff58a2a'
down_revision: Union[str, None] = 'b0f845e1039d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
