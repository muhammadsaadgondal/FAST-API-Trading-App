"""Migration test

Revision ID: ca81f8d3f6cb
Revises: 7a58c138c236
Create Date: 2024-11-02 00:01:53.241335

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ca81f8d3f6cb'
down_revision: Union[str, None] = '7a58c138c236'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
