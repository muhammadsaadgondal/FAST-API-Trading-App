"""Migration not being performed

Revision ID: 7a58c138c236
Revises: 664fbb528e10
Create Date: 2024-11-01 23:58:58.975583

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a58c138c236'
down_revision: Union[str, None] = '664fbb528e10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
