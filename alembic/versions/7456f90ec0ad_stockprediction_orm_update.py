"""StockPrediction ORM update

Revision ID: 7456f90ec0ad
Revises: 693453e070c3
Create Date: 2024-11-01 00:54:11.151807

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7456f90ec0ad'
down_revision: Union[str, None] = '693453e070c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
