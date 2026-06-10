"""add phone_number to agents

Revision ID: 79aeb699f367
Revises: 9bc107bac502
Create Date: 2026-06-10 17:52:00.894321

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '79aeb699f367'
down_revision: Union[str, Sequence[str], None] = '9bc107bac502'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('agents', sa.Column('phone_number', sa.String(), nullable=True))

def downgrade() -> None:
    op.drop_column('agents', 'phone_number')