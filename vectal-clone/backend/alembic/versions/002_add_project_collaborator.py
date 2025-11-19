"""add project collaborator model

Revision ID: 002
Revises: 001
Create Date: 2025-11-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create project_collaborators table
    op.create_table(
        'project_collaborators',
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='viewer'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('invited_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['invited_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('project_id', 'user_id')
    )
    
    # Create indexes
    op.create_index('idx_collaborator_project', 'project_collaborators', ['project_id'])
    op.create_index('idx_collaborator_user', 'project_collaborators', ['user_id'])
    op.create_index('idx_collaborator_status', 'project_collaborators', ['status'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_collaborator_status', table_name='project_collaborators')
    op.drop_index('idx_collaborator_user', table_name='project_collaborators')
    op.drop_index('idx_collaborator_project', table_name='project_collaborators')
    
    # Drop table
    op.drop_table('project_collaborators')
