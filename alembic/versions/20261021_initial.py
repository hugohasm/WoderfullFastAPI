"""initial schema

Revision ID: 20261021_01
Revises: 
Create Date: 2026-10-21 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20261021_01'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm;')
    op.execute('CREATE EXTENSION IF NOT EXISTS unaccent;')

    op.create_table(
        'clinics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('normalized_name', sa.String(length=255), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('normalized_location', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_clinics_id'), 'clinics', ['id'], unique=False)
    op.create_index(op.f('ix_clinics_normalized_name'), 'clinics', ['normalized_name'], unique=False)
    op.create_index(op.f('ix_clinics_normalized_location'), 'clinics', ['normalized_location'], unique=False)
    op.create_index('idx_clinics_name_trgm', 'clinics', ['normalized_name'], unique=False, postgresql_using='gin', postgresql_ops={'normalized_name': 'gin_trgm_ops'})
    op.create_index('idx_clinics_location_trgm', 'clinics', ['normalized_location'], unique=False, postgresql_using='gin', postgresql_ops={'normalized_location': 'gin_trgm_ops'})

    op.create_table(
        'sync_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('total_records_received', sa.Integer(), nullable=False),
        sa.Column('total_records_processed', sa.Integer(), nullable=False),
        sa.Column('total_records_rejected', sa.Integer(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_sync_runs_id'), 'sync_runs', ['id'], unique=False)

    op.create_table(
        'doctors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_record_key', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column('last_name', sa.String(length=255), nullable=True),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('normalized_full_name', sa.String(length=255), nullable=False),
        sa.Column('speciality', sa.String(length=255), nullable=True),
        sa.Column('normalized_speciality', sa.String(length=255), nullable=True),
        sa.Column('clinic_id', sa.Integer(), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('normalized_location', sa.String(length=255), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(length=64), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('postal_code', sa.String(length=32), nullable=True),
        sa.Column('county', sa.String(length=128), nullable=True),
        sa.Column('years_experience', sa.Integer(), nullable=True),
        sa.Column('education', sa.Text(), nullable=True),
        sa.Column('languages', sa.Text(), nullable=True),
        sa.Column('availability', sa.Text(), nullable=True),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['clinic_id'], ['clinics.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source_record_key', name='uq_doctors_source_record_key'),
    )
    op.create_index(op.f('ix_doctors_id'), 'doctors', ['id'], unique=False)
    op.create_index(op.f('ix_doctors_source_record_key'), 'doctors', ['source_record_key'], unique=False)
    op.create_index(op.f('ix_doctors_normalized_full_name'), 'doctors', ['normalized_full_name'], unique=False)
    op.create_index(op.f('ix_doctors_normalized_speciality'), 'doctors', ['normalized_speciality'], unique=False)
    op.create_index(op.f('ix_doctors_normalized_location'), 'doctors', ['normalized_location'], unique=False)
    op.create_index(op.f('ix_doctors_clinic_id'), 'doctors', ['clinic_id'], unique=False)
    op.create_index('idx_doctors_name_trgm', 'doctors', ['normalized_full_name'], unique=False, postgresql_using='gin', postgresql_ops={'normalized_full_name': 'gin_trgm_ops'})
    op.create_index('idx_doctors_speciality_trgm', 'doctors', ['normalized_speciality'], unique=False, postgresql_using='gin', postgresql_ops={'normalized_speciality': 'gin_trgm_ops'})
    op.create_index('idx_doctors_location_trgm', 'doctors', ['normalized_location'], unique=False, postgresql_using='gin', postgresql_ops={'normalized_location': 'gin_trgm_ops'})


def downgrade() -> None:
    op.drop_index('idx_doctors_location_trgm', table_name='doctors')
    op.drop_index('idx_doctors_speciality_trgm', table_name='doctors')
    op.drop_index('idx_doctors_name_trgm', table_name='doctors')
    op.drop_index(op.f('ix_doctors_clinic_id'), table_name='doctors')
    op.drop_index(op.f('ix_doctors_normalized_location'), table_name='doctors')
    op.drop_index(op.f('ix_doctors_normalized_speciality'), table_name='doctors')
    op.drop_index(op.f('ix_doctors_normalized_full_name'), table_name='doctors')
    op.drop_index(op.f('ix_doctors_source_record_key'), table_name='doctors')
    op.drop_index(op.f('ix_doctors_id'), table_name='doctors')
    op.drop_table('doctors')
    op.drop_index(op.f('ix_sync_runs_id'), table_name='sync_runs')
    op.drop_table('sync_runs')
    op.drop_index('idx_clinics_location_trgm', table_name='clinics')
    op.drop_index('idx_clinics_name_trgm', table_name='clinics')
    op.drop_index(op.f('ix_clinics_normalized_location'), table_name='clinics')
    op.drop_index(op.f('ix_clinics_normalized_name'), table_name='clinics')
    op.drop_index(op.f('ix_clinics_id'), table_name='clinics')
    op.drop_table('clinics')
