"""Form attribute set True

Revision ID: 17daa28cc054
Revises: c05440c5801b
Create Date: 2024-11-01 15:42:01.229388

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '17daa28cc054'
down_revision: Union[str, None] = 'c05440c5801b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
