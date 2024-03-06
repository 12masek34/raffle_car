create_raffle = """
    CREATE TABLE IF NOT EXISTS raffle (
        id BIGSERIAL PRIMARY KEY,
        user_id BIGINT,
        user_login TEXT,
        user_name TEXT
    );
"""
insert_raffle = """
    INSERT INTO raffle (user_id, user_login, user_name) values ($1, $2, $3) RETURNING id
"""