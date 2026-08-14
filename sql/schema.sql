-- Auto-generated PostgreSQL schema.
-- Source: LH Nautical CSV files.

CREATE TABLE IF NOT EXISTS "addresses" (
    "id" BIGINT,
    "customer_id" BIGINT,
    "address_type" TEXT,
    "postal_code" TEXT,
    "street" TEXT,
    "number" TEXT,
    "complement" TEXT,
    "district" TEXT,
    "city" TEXT,
    "state" TEXT,
    "country" TEXT,
    "is_primary" BOOLEAN
);

CREATE TABLE IF NOT EXISTS "attributes" (
    "id" BIGINT,
    "name" TEXT,
    "data_type" TEXT
);

CREATE TABLE IF NOT EXISTS "brands" (
    "id" BIGINT,
    "name" TEXT,
    "country" TEXT,
    "is_active" BOOLEAN,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "categories" (
    "id" BIGINT,
    "name" TEXT,
    "slug" TEXT,
    "parent_category_id" BIGINT,
    "is_active" BOOLEAN,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "customers" (
    "id" BIGINT,
    "person_type" TEXT,
    "legal_name" TEXT,
    "trade_name" TEXT,
    "tax_id" TEXT,
    "state_registration" TEXT,
    "email" TEXT,
    "phone" TEXT,
    "is_active" BOOLEAN,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "employees" (
    "id" BIGINT,
    "full_name" TEXT,
    "cpf" TEXT,
    "email" TEXT,
    "role" TEXT,
    "primary_location_id" BIGINT,
    "hire_date" DATE,
    "termination_date" DATE,
    "is_active" BOOLEAN,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "fiscal_invoices" (
    "id" BIGINT,
    "order_id" BIGINT,
    "nfe_number" TEXT,
    "nfe_access_key" TEXT,
    "series" TEXT,
    "issued_at" TIMESTAMP,
    "status" TEXT,
    "total_amount" NUMERIC,
    "xml_storage_uri" TEXT,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "goods_receipt_items" (
    "id" BIGINT,
    "goods_receipt_id" BIGINT,
    "purchase_order_item_id" BIGINT,
    "quantity_received" NUMERIC
);

CREATE TABLE IF NOT EXISTS "goods_receipts" (
    "id" BIGINT,
    "purchase_order_id" BIGINT,
    "received_by_employee_id" BIGINT,
    "received_at" TIMESTAMP,
    "notes" TEXT,
    "created_at" TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "locations" (
    "id" BIGINT,
    "name" TEXT,
    "location_type" TEXT,
    "postal_code" TEXT,
    "street" TEXT,
    "number" TEXT,
    "complement" TEXT,
    "district" TEXT,
    "city" TEXT,
    "state" TEXT,
    "country" TEXT,
    "is_active" BOOLEAN,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "order_items" (
    "id" BIGINT,
    "order_id" BIGINT,
    "product_variant_id" BIGINT,
    "quantity" BIGINT,
    "unit_price" NUMERIC,
    "icms_rate" NUMERIC,
    "ipi_rate" NUMERIC,
    "line_total" NUMERIC
);

CREATE TABLE IF NOT EXISTS "orders" (
    "id" BIGINT,
    "order_number" TEXT,
    "channel" TEXT,
    "customer_id" BIGINT,
    "salesperson_id" BIGINT,
    "location_id" BIGINT,
    "status" TEXT,
    "subtotal" NUMERIC,
    "discount_amount" NUMERIC,
    "total" NUMERIC,
    "placed_at" TIMESTAMP,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "payments" (
    "id" BIGINT,
    "order_id" BIGINT,
    "method" TEXT,
    "installments" BIGINT,
    "amount" NUMERIC,
    "status" TEXT,
    "paid_at" TIMESTAMP,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "product_suppliers" (
    "product_variant_id" BIGINT,
    "supplier_id" BIGINT,
    "supplier_sku" TEXT,
    "last_quoted_cost" NUMERIC,
    "lead_time_days" BIGINT,
    "is_preferred" BOOLEAN,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "product_variants" (
    "id" BIGINT,
    "product_id" BIGINT,
    "sku" TEXT,
    "barcode_ean" TEXT,
    "sale_price" NUMERIC,
    "cost_price" NUMERIC,
    "weight_kg" NUMERIC,
    "icms_rate" NUMERIC,
    "ipi_rate" NUMERIC,
    "is_active" BOOLEAN,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "products" (
    "id" BIGINT,
    "name" TEXT,
    "description" TEXT,
    "brand_id" BIGINT,
    "category_id" BIGINT,
    "ncm_code" TEXT,
    "unit_of_measure" TEXT,
    "is_active" BOOLEAN,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "purchase_order_items" (
    "id" BIGINT,
    "purchase_order_id" BIGINT,
    "product_variant_id" BIGINT,
    "quantity_ordered" BIGINT,
    "unit_cost" NUMERIC,
    "line_total" NUMERIC
);

CREATE TABLE IF NOT EXISTS "purchase_orders" (
    "id" BIGINT,
    "po_number" TEXT,
    "supplier_id" BIGINT,
    "buyer_id" BIGINT,
    "destination_location_id" BIGINT,
    "status" TEXT,
    "currency" TEXT,
    "subtotal" NUMERIC,
    "total" NUMERIC,
    "placed_at" TIMESTAMP,
    "expected_delivery_at" DATE,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "return_items" (
    "id" BIGINT,
    "return_id" BIGINT,
    "order_item_id" BIGINT,
    "quantity" NUMERIC,
    "action" TEXT,
    "exchange_variant_id" BIGINT,
    "unit_refund_amount" NUMERIC
);

CREATE TABLE IF NOT EXISTS "returns" (
    "id" BIGINT,
    "return_number" TEXT,
    "order_id" BIGINT,
    "customer_id" BIGINT,
    "received_at_location_id" BIGINT,
    "status" TEXT,
    "reason" TEXT,
    "total_refund_amount" NUMERIC,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "stock_levels" (
    "product_variant_id" BIGINT,
    "location_id" BIGINT,
    "quantity_on_hand" NUMERIC,
    "reorder_point" TEXT,
    "updated_at" TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "stock_movements" (
    "id" BIGINT,
    "product_variant_id" BIGINT,
    "location_id" BIGINT,
    "movement_type" TEXT,
    "quantity" NUMERIC,
    "reference_table" TEXT,
    "reference_id" BIGINT,
    "employee_id" BIGINT,
    "notes" TEXT,
    "occurred_at" TIMESTAMP,
    "created_at" TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "suppliers" (
    "id" BIGINT,
    "legal_name" TEXT,
    "trade_name" TEXT,
    "country" TEXT,
    "tax_id" TEXT,
    "tax_id_type" TEXT,
    "email" TEXT,
    "phone" TEXT,
    "contact_name" TEXT,
    "is_active" BOOLEAN,
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "variant_attribute_values" (
    "product_variant_id" BIGINT,
    "attribute_id" BIGINT,
    "value" TEXT
);
