"""Prection model update

Revision ID: 8b95ce9336ae
Revises: 5381134b585a
Create Date: 2024-11-01 02:16:05.920236

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b95ce9336ae'
down_revision: Union[str, None] = '5381134b585a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
