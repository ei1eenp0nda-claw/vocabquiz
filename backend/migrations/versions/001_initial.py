"""Initial migration - Create all tables

Revision ID: 001
Revises: 
Create Date: 2026-03-13 11:55:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(length=80), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=128), nullable=False),
        sa.Column('avatar_url', sa.String(length=255), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Create notes table
    op.create_table('notes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('tags', sa.String(length=500), nullable=True),
        sa.Column('cover_image', sa.String(length=255), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notes_created_at'), 'notes', ['created_at'], unique=False)
    op.create_index(op.f('ix_notes_status'), 'notes', ['status'], unique=False)
    op.create_index(op.f('ix_notes_user_id'), 'notes', ['user_id'], unique=False)
    
    # Create likes table
    op.create_table('likes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('note_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['note_id'], ['notes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'note_id', name='unique_user_note_like')
    )
    op.create_index(op.f('ix_likes_note_id'), 'likes', ['note_id'], unique=False)
    op.create_index(op.f('ix_likes_user_id'), 'likes', ['user_id'], unique=False)
    
    # Create favorites table
    op.create_table('favorites',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('note_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['note_id'], ['notes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'note_id', name='unique_user_note_favorite')
    )
    op.create_index(op.f('ix_favorites_note_id'), 'favorites', ['note_id'], unique=False)
    op.create_index(op.f('ix_favorites_user_id'), 'favorites', ['user_id'], unique=False)
    
    # Create comments table
    op.create_table('comments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('note_id', sa.Integer(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['note_id'], ['notes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['comments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comments_note_id'), 'comments', ['note_id'], unique=False)
    op.create_index(op.f('ix_comments_parent_id'), 'comments', ['parent_id'], unique=False)
    op.create_index(op.f('ix_comments_user_id'), 'comments', ['user_id'], unique=False)
    
    # Create follows table
    op.create_table('follows',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('follower_id', sa.Integer(), nullable=False),
        sa.Column('followed_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['followed_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['follower_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('follower_id', 'followed_id', name='unique_follow')
    )
    op.create_index(op.f('ix_follows_followed_id'), 'follows', ['followed_id'], unique=False)
    op.create_index(op.f('ix_follows_follower_id'), 'follows', ['follower_id'], unique=False)


def downgrade() -> None:
    op.drop_table('follows')
    op.drop_table('comments')
    op.drop_table('favorites')
    op.drop_table('likes')
    op.drop_table('notes')
    op.drop_table('users')
