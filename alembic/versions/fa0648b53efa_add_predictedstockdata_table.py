"""Add PredictedStockData table

Revision ID: fa0648b53efa
Revises: 3bb5f59f5f99
Create Date: 2024-10-30 22:15:38.417865

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa0648b53efa'
down_revision: Union[str, None] = '3bb5f59f5f99'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
