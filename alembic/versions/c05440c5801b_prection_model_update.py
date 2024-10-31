"""Prection model update

Revision ID: c05440c5801b
Revises: 8b95ce9336ae
Create Date: 2024-11-01 02:18:07.176171

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c05440c5801b'
down_revision: Union[str, None] = '8b95ce9336ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
