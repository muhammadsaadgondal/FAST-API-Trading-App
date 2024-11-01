"""Description of your migratiodn

Revision ID: 664fbb528e10
Revises: cda44ea94935
Create Date: 2024-11-01 23:57:32.486371

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '664fbb528e10'
down_revision: Union[str, None] = 'cda44ea94935'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
