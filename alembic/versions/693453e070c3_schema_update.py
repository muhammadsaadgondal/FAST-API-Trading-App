"""Schema update

Revision ID: 693453e070c3
Revises: fa0648b53efa
Create Date: 2024-10-31 00:47:14.118717

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '693453e070c3'
down_revision: Union[str, None] = 'fa0648b53efa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
