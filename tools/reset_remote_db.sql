-- This script resets the remote database by truncating all tables.
TRUNCATE TABLE
    buyers,
    images,
    metadata,
    product_images,
    products,
    purchases
RESTART IDENTITY CASCADE;
