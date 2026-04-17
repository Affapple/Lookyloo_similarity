CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE images (
    uniq_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    uid uuid NOT NULL,
    sha256 VARCHAR(64),
    meta_information JSONB,
    metadata JSONB NOT NULL,
    analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE hashes(
    uniq_id uuid PRIMARY KEY,
    embedding VARCHAR(2048) NOT NULL,

    FOREIGN KEY(uniq_id) REFERENCES images(uniq_id)
);
