"""Test run

Revision ID: 857ddbacda80
Revises: af19eff58a2a
Create Date: 2024-11-01 23:50:24.650256

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '857ddbacda80'
down_revision: Union[str, None] = 'af19eff58a2a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
