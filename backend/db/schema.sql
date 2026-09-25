CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- SHOPS
-- ============================================

CREATE TABLE IF NOT EXISTS shops (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(30),
    email VARCHAR(255),
    address TEXT,
    timezone VARCHAR(50) NOT NULL DEFAULT 'America/Chicago',

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- BARBERS
-- ============================================

CREATE TABLE IF NOT EXISTS barbers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,

    name VARCHAR(255) NOT NULL,
    phone VARCHAR(30),
    email VARCHAR(255),

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_barbers_shop_id
ON barbers(shop_id);

CREATE UNIQUE INDEX IF NOT EXISTS
idx_barbers_shop_name_unique
ON barbers (shop_id, LOWER(name));

CREATE UNIQUE INDEX IF NOT EXISTS
idx_barbers_shop_phone_unique
ON barbers (shop_id, phone)
WHERE phone IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS
idx_barbers_shop_email_unique
ON barbers (shop_id, LOWER(email))
WHERE email IS NOT NULL;

-- ============================================
-- SERVICES
-- ============================================

CREATE TABLE IF NOT EXISTS services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,

    name VARCHAR(255) NOT NULL,
    description TEXT,

    duration_minutes INTEGER NOT NULL CHECK (duration_minutes > 0),
    price_cents INTEGER NOT NULL CHECK (price_cents >= 0),

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_services_shop_id
ON services(shop_id);

-- ============================================
-- CUSTOMERS
-- ============================================

CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,

    name VARCHAR(255) NOT NULL,
    phone VARCHAR(30) NOT NULL,
    email VARCHAR(255),

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(shop_id, phone)
);

CREATE INDEX IF NOT EXISTS idx_customers_shop_id
ON customers(shop_id);

-- ============================================
-- BUSINESS HOURS
-- ============================================

CREATE TABLE IF NOT EXISTS business_hours (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,

    -- 0 = Sunday, 1 = Monday ... 6 = Saturday
    day_of_week INTEGER NOT NULL CHECK (
        day_of_week >= 0 AND day_of_week <= 6
    ),

    open_time TIME,
    close_time TIME,

    is_closed BOOLEAN NOT NULL DEFAULT FALSE,

    UNIQUE(shop_id, day_of_week)
);

CREATE INDEX IF NOT EXISTS idx_business_hours_shop_id
ON business_hours(shop_id);

-- ============================================
-- BARBER HOURS
-- ============================================

CREATE TABLE IF NOT EXISTS barber_hours (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    barber_id UUID NOT NULL REFERENCES barbers(id) ON DELETE CASCADE,

    day_of_week INTEGER NOT NULL CHECK (
        day_of_week >= 0 AND day_of_week <= 6
    ),

    start_time TIME,
    end_time TIME,

    is_off BOOLEAN NOT NULL DEFAULT FALSE,

    UNIQUE(barber_id, day_of_week)
);

CREATE INDEX IF NOT EXISTS idx_barber_hours_barber_id
ON barber_hours(barber_id);

-- ============================================
-- SHOP CLOSURES / HOLIDAYS
-- ============================================

CREATE TABLE IF NOT EXISTS shop_closures (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    closure_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    reason VARCHAR(255),
    closure_type VARCHAR(30) NOT NULL DEFAULT 'HOLIDAY',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (
        (start_time IS NULL AND end_time IS NULL)
        OR
        (start_time IS NOT NULL AND end_time IS NOT NULL AND end_time > start_time)
    ),

    CHECK (
        closure_type IN ('HOLIDAY', 'EMERGENCY', 'OTHER')
    )
);

CREATE INDEX IF NOT EXISTS idx_shop_closures_shop_date
ON shop_closures(shop_id, closure_date);

-- ============================================
-- APPOINTMENTS
-- ============================================

CREATE TABLE IF NOT EXISTS appointments (

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shop_id UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES customers(id),
    barber_id UUID REFERENCES barbers(id),
    service_id UUID NOT NULL REFERENCES services(id),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'BOOKED',
    customer_status VARCHAR(30),
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (end_time > start_time)
);

CREATE INDEX IF NOT EXISTS idx_appointments_shop_start
ON appointments(shop_id, start_time);

CREATE INDEX IF NOT EXISTS idx_appointments_barber_start
ON appointments(barber_id, start_time);

CREATE INDEX IF NOT EXISTS idx_appointments_customer
ON appointments(customer_id);

-- ============================================
-- NOTIFICATIONS
-- ============================================

CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    appointment_id UUID NOT NULL
        REFERENCES appointments(id)
        ON DELETE CASCADE,

    type VARCHAR(50) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    recipient_type VARCHAR(20) NOT NULL,
    recipient_id UUID,
    recipient VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    scheduled_for TIMESTAMP,
    sent_at TIMESTAMP,
    failed_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT notifications_type_check
        CHECK (
            type IN (
                'confirmation',
                'rescheduled',
                'cancelled',
                'reminder'
            )
        ),

    CONSTRAINT notifications_channel_check
        CHECK (
            channel IN (
                'sms',
                'email'
            )
        ),

    CONSTRAINT notifications_recipient_type_check
        CHECK (
            recipient_type IN (
                'customer',
                'barber',
                'shop'
            )
        ),

    CONSTRAINT notifications_status_check
        CHECK (
            status IN (
                'pending',
                'sent',
                'failed'
            )
        )
);

CREATE INDEX IF NOT EXISTS idx_notifications_appointment_id
ON notifications(appointment_id);

CREATE INDEX IF NOT EXISTS idx_notifications_recipient_id
ON notifications(recipient_id);

CREATE INDEX IF NOT EXISTS idx_notifications_status_scheduled
ON notifications(status, scheduled_for);
