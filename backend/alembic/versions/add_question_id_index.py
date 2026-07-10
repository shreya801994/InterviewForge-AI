# revision identifiers, used by Alembic.
revision = 'add_question_id_index'
down_revision = '1a2b3c4d5e6f'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add index on interview_messages.question_id for faster lookups
    op.create_index('ix_interview_messages_question_id', 'interview_messages', ['question_id'], unique=False)

def downgrade():
    op.drop_index('ix_interview_messages_question_id', table_name='interview_messages')
