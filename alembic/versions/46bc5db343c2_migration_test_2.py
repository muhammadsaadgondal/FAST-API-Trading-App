"""Migration test 2

Revision ID: 46bc5db343c2
Revises: ca81f8d3f6cb
Create Date: 2024-11-02 00:04:35.712327

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '46bc5db343c2'
down_revision: Union[str, None] = 'ca81f8d3f6cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
