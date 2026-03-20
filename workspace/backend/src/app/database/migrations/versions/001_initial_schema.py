"""Initial schema creation."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

def upgrade():
    # Users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100)),
        sa.Column('last_name', sa.String(100)),
        sa.Column('avatar_url', sa.String(500)),
        sa.Column('gender', sa.String(50)),
        sa.Column('age_range', sa.String(50)),
        sa.Column('height_cm', sa.Integer),
        sa.Column('preferred_fit', sa.String(50)),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('email_verified', sa.Boolean, server_default='false'),
        sa.Column('receives_marketing', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('last_login_at', sa.DateTime),
        sa.Column('deleted_at', sa.DateTime),
    )
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_created_at', 'users', ['created_at'], postgresql_desc=True)

    # Scans table
    op.create_table(
        'scans',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), server_default='My Scan'),
        sa.Column('scan_type', sa.String(50), nullable=False),
        sa.Column('scan_file_key', sa.String(500)),
        sa.Column('rigged_file_key', sa.String(500)),
        sa.Column('status', sa.String(50), server_default='pending'),
        sa.Column('error_message', sa.Text),
        sa.Column('body_shape', sa.String(100)),
        sa.Column('confidence_score', sa.Float),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_scans_user_id', 'scans', ['user_id'])
    op.create_index('idx_scans_status', 'scans', ['status'])

    # Scan measurements table
    op.create_table(
        'scan_measurements',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('scan_id', UUID(as_uuid=True), nullable=False),
        sa.Column('chest_cm', sa.Float),
        sa.Column('waist_cm', sa.Float),
        sa.Column('hips_cm', sa.Float),
        sa.Column('inseam_cm', sa.Float),
        sa.Column('shoulder_width_cm', sa.Float),
        sa.Column('arm_length_cm', sa.Float),
        sa.Column('torso_length_cm', sa.Float),
        sa.Column('weight_kg', sa.Float),
        sa.Column('bmi', sa.Float),
        sa.Column('fit_profile_notes', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ondelete='CASCADE'),
    )

    # Garment categories table
    op.create_table(
        'garment_categories',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text),
        sa.Column('parent_id', UUID(as_uuid=True)),
        sa.Column('sort_order', sa.Integer),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['parent_id'], ['garment_categories.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_garment_categories_slug', 'garment_categories', ['slug'])

    # Retail partners table
    op.create_table(
        'retail_partners',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('name', sa.String(100)),
        sa.Column('slug', sa.String(100), nullable=False, unique=True),
        sa.Column('api_endpoint', sa.String(500)),
        sa.Column('api_key_hash', sa.String(255)),
        sa.Column('is_active', sa.Boolean, server_default='false'),
        sa.Column('contact_email', sa.String(255)),
        sa.Column('integration_type', sa.String(50)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('idx_retail_partners_slug', 'retail_partners', ['slug'])

    # Garments table
    op.create_table(
        'garments',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('sku', sa.String(100), nullable=False, unique=True),
        sa.Column('brand_id', UUID(as_uuid=True)),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('category_id', UUID(as_uuid=True)),
        sa.Column('garment_type', sa.String(50), nullable=False),
        sa.Column('model_file_key', sa.String(500), nullable=False),
        sa.Column('texture_urls', sa.JSON),
        sa.Column('fit_category', sa.String(50)),
        sa.Column('fabric_type', sa.String(100)),
        sa.Column('fabric_weight_gsm', sa.Float),
        sa.Column('fabric_stretch_percent', sa.Float),
        sa.Column('price_usd', sa.Float),
        sa.Column('retail_url', sa.String(500)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime),
        sa.ForeignKeyConstraint(['brand_id'], ['retail_partners.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['garment_categories.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_garments_sku', 'garments', ['sku'])
    op.create_index('idx_garments_brand_id', 'garments', ['brand_id'])

    # Garment sizes table
    op.create_table(
        'garment_sizes',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('garment_id', UUID(as_uuid=True), nullable=False),
        sa.Column('size_label', sa.String(50), nullable=False),
        sa.Column('size_order', sa.Integer),
        sa.Column('chest_min_cm', sa.Float),
        sa.Column('chest_max_cm', sa.Float),
        sa.Column('waist_min_cm', sa.Float),
        sa.Column('waist_max_cm', sa.Float),
        sa.Column('hips_min_cm', sa.Float),
        sa.Column('hips_max_cm', sa.Float),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['garment_id'], ['garments.id'], ondelete='CASCADE'),
    )

    # Outfits table
    op.create_table(
        'outfits',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('scan_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('is_private', sa.Boolean, server_default='true'),
        sa.Column('occasions', sa.String(500)),
        sa.Column('mood', sa.String(100)),
        sa.Column('preview_image_url', sa.String(500)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_outfits_user_id', 'outfits', ['user_id'])

    # Outfit items table
    op.create_table(
        'outfit_items',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('outfit_id', UUID(as_uuid=True), nullable=False),
        sa.Column('garment_id', UUID(as_uuid=True), nullable=False),
        sa.Column('garment_size_id', UUID(as_uuid=True)),
        sa.Column('display_order', sa.Integer),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['outfit_id'], ['outfits.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['garment_id'], ['garments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['garment_size_id'], ['garment_sizes.id'], ondelete='SET NULL'),
    )

    # Saved favourite garments table
    op.create_table(
        'saved_favourite_garments',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('garment_id', UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['garment_id'], ['garments.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_saved_favourite_garments_user_id', 'saved_favourite_garments', ['user_id'])


def downgrade():
    op.drop_table('saved_favourite_garments')
    op.drop_table('outfit_items')
    op.drop_table('outfits')
    op.drop_table('garment_sizes')
    op.drop_table('garments')
    op.drop_table('retail_partners')
    op.drop_table('garment_categories')
    op.drop_table('scan_measurements')
    op.drop_table('scans')
    op.drop_table('users')
