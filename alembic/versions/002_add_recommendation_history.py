"""add recommendation history table

Revision ID: 002
Revises: 001
Create Date: 2024-12-30 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # RecommendationHistory 테이블 생성
    op.create_table(
        'recommendation_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('request_type', sa.String(length=32), nullable=False),
        sa.Column('input_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('result_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recommendation_history_id'), 'recommendation_history', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_recommendation_history_id'), table_name='recommendation_history')
    op.drop_table('recommendation_history') 