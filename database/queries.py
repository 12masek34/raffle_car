create_raffle = """
    CREATE TABLE IF NOT EXISTS raffle (
        id BIGSERIAL PRIMARY KEY,
        user_id BIGINT,
        user_login TEXT,
        user_name TEXT,
        shirt TEXT,
        size TEXT,
        photo_ids TEXT[],
        document_ids TEXT[],
        video_ids TEXT[],
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        aprove BOOLEAN NOT NULL DEFAULT false
    );
"""

insert_raffle = """
    INSERT INTO raffle (user_id, user_login, user_name) values ($1, $2, $3) RETURNING id
"""

insert_field = """
    UPDATE raffle SET {field} = $2
    WHERE id = (SELECT id FROM raffle WHERE user_id = $1 ORDER BY id DESC LIMIT 1)
"""

select_documents = """
    SELECT photo_ids, document_ids, video_ids FROM raffle
    WHERE id = (SELECT id FROM raffle WHERE user_id = $1 ORDER BY id DESC LIMIT 1)
"""

insert_document = """
    UPDATE raffle
    SET document_ids = array_append(document_ids, $2),
    photo_ids = array_append(photo_ids, $3),
    video_ids = array_append(video_ids, $4)
    WHERE id = (SELECT id FROM raffle WHERE user_id = $1 ORDER BY id DESC LIMIT 1)
"""

select_order = """
    SELECT
        id,
        user_id,
        user_login,
        user_name,
        shirt,
        size
    FROM raffle WHERE id = (SELECT id FROM raffle WHERE user_id = $1 ORDER BY id DESC LIMIT 1)
"""

select_report = """
    SELECT
        id,
        user_id,
        user_login,
        user_name,
        shirt,
        size,
        created_at
    FROM raffle
    WHERE aprove = true
    ORDER BY id
"""
update_status = """
    UPDATE raffle
    SET aprove = true
    WHERE id = $1
    RETURNING id
"""