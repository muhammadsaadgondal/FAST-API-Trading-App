"""Final update

Revision ID: 6334a4fb866c
Revises: 17daa28cc054
Create Date: 2024-11-01 23:43:28.439634

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6334a4fb866c'
down_revision: Union[str, None] = '17daa28cc054'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
