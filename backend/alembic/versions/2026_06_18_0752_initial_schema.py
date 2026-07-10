"""Initial schema

Revision ID: 1a2b3c4d5e6f
Revises: None
Create Date: 2026-06-18 07:52:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '1a2b3c4d5e6f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=150), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. Resumes table
    op.create_table(
        'resumes',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('parsed_text', sa.Text(), nullable=True),
        sa.Column('skills', sa.JSON(), nullable=True),
        sa.Column('projects', sa.JSON(), nullable=True),
        sa.Column('strengths', sa.JSON(), nullable=True),
        sa.Column('focus_areas', sa.JSON(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_resumes_user_id', 'resumes', ['user_id'], unique=False)
    op.create_index('ix_resumes_uploaded_at', 'resumes', ['uploaded_at'], unique=False)

    # 3. Question Bank table
    op.create_table(
        'question_bank',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('topic', sa.String(length=100), nullable=False),
        sa.Column('difficulty', sa.String(length=50), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('expected_keywords', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 4. Interview Sessions table
    op.create_table(
        'interview_sessions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('role', sa.String(length=100), nullable=False),
        sa.Column('difficulty', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('question_count', sa.Integer(), nullable=True),
        sa.Column('focus_topics', sa.JSON(), nullable=True),
        sa.Column('questions_answered', sa.Integer(), nullable=True),
        sa.Column('average_score', sa.Float(), nullable=True),
        sa.Column('completion_percentage', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_interview_sessions_user_id', 'interview_sessions', ['user_id'], unique=False)
    op.create_index('ix_interview_sessions_started_at', 'interview_sessions', ['started_at'], unique=False)

    # 5. Interview Messages table
    op.create_table(
        'interview_messages',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('session_id', sa.String(length=36), nullable=False),
        sa.Column('message_type', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('question_id', sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['interview_sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_id'], ['question_bank.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_interview_messages_session_id', 'interview_messages', ['session_id'], unique=False)
    op.create_index('ix_interview_messages_created_at', 'interview_messages', ['created_at'], unique=False)

    # 6. Reports table
    op.create_table(
        'reports',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('session_id', sa.String(length=36), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('strengths', sa.JSON(), nullable=True),
        sa.Column('weaknesses', sa.JSON(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('roadmap', sa.JSON(), nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('report_version', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['interview_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id')
    )
    op.create_index('ix_reports_session_id', 'reports', ['session_id'], unique=True)

    # 7. Skill Scores table
    op.create_table(
        'skill_scores',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('skill_name', sa.String(length=100), nullable=False),
        sa.Column('technical_avg', sa.Float(), nullable=True),
        sa.Column('communication_avg', sa.Float(), nullable=True),
        sa.Column('depth_avg', sa.Float(), nullable=True),
        sa.Column('overall_avg', sa.Float(), nullable=True),
        sa.Column('attempt_count', sa.Integer(), nullable=True),
        sa.Column('last_score', sa.Float(), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'skill_name', name='uq_user_skill')
    )
    op.create_index('ix_skill_scores_user_id', 'skill_scores', ['user_id'], unique=False)
    op.create_index('ix_skill_scores_last_updated', 'skill_scores', ['last_updated'], unique=False)

def downgrade() -> None:
    op.drop_table('skill_scores')
    op.drop_table('reports')
    op.drop_table('interview_messages')
    op.drop_table('interview_sessions')
    op.drop_table('question_bank')
    op.drop_table('resumes')
    op.drop_table('users')
