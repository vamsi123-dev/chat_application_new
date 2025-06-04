"""initial migration

Revision ID: initial_migration
Revises: 
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'initial_migration'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create orders table
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.String(), nullable=False),
        sa.Column('customer_id', sa.String(), nullable=False),
        sa.Column('service_provider_id', sa.String(), nullable=False),
        sa.Column('service_type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_id')
    )
    op.create_index('ix_orders_order_id', 'orders', ['order_id'])
    op.create_index('ix_orders_customer_id', 'orders', ['customer_id'])
    op.create_index('ix_orders_service_provider_id', 'orders', ['service_provider_id'])

    # Create chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.String(), nullable=False),
        sa.Column('sender_id', sa.String(), nullable=False),
        sa.Column('receiver_id', sa.String(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('message_type', sa.String(), nullable=False),
        sa.Column('is_read', sa.Integer(), nullable=False, default=0),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_chat_messages_order_id', 'chat_messages', ['order_id'])
    op.create_index('ix_chat_messages_sender_id', 'chat_messages', ['sender_id'])
    op.create_index('ix_chat_messages_receiver_id', 'chat_messages', ['receiver_id'])

def downgrade() -> None:
    op.drop_table('chat_messages')
    op.drop_table('orders') 