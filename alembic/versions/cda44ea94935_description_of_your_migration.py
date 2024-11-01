"""Description of your migration

Revision ID: cda44ea94935
Revises: 857ddbacda80
Create Date: 2024-11-01 23:52:08.327970

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cda44ea94935'
down_revision: Union[str, None] = '857ddbacda80'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
