"""model update

Revision ID: 5381134b585a
Revises: 7456f90ec0ad
Create Date: 2024-11-01 01:02:33.711106

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5381134b585a'
down_revision: Union[str, None] = '7456f90ec0ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
