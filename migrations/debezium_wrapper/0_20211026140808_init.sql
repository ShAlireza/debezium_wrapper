-- upgrade --
CREATE TABLE IF NOT EXISTS "debezium_wrapper.cronjob" (
    "id" VARCHAR(48) NOT NULL  PRIMARY KEY,
    "enable" BOOL NOT NULL  DEFAULT True,
    "host" VARCHAR(128) NOT NULL,
    "port" INT NOT NULL  DEFAULT 80,
    "minute" VARCHAR(16) NOT NULL  DEFAULT '*',
    "hour" VARCHAR(16) NOT NULL  DEFAULT '*',
    "day_of_month" VARCHAR(16) NOT NULL  DEFAULT '*',
    "month" VARCHAR(16) NOT NULL  DEFAULT '*',
    "day_of_week" VARCHAR(16) NOT NULL  DEFAULT '*',
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "full_command" VARCHAR(512)
);
CREATE TABLE IF NOT EXISTS "debezium_wrapper.kafkaconnect" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "host" VARCHAR(128) NOT NULL,
    "port" INT NOT NULL  DEFAULT 8083
);
CREATE TABLE IF NOT EXISTS "debezium_wrapper.connector" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(256) NOT NULL,
    "kind" VARCHAR(256) NOT NULL,
    "config" JSONB NOT NULL,
    "kafka_connect_id" INT NOT NULL REFERENCES "debezium_wrapper.kafkaconnect" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "debezium_wrapper.statusattempt" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL,
    "has_failed_task" BOOL NOT NULL  DEFAULT False,
    "number_of_tasks" SMALLINT NOT NULL  DEFAULT 1,
    "connect_id" INT NOT NULL REFERENCES "debezium_wrapper.connector" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "debezium_wrapper.TaskModel" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "task_id" SMALLINT NOT NULL  DEFAULT 0,
    "connector_id" INT NOT NULL REFERENCES "debezium_wrapper.connector" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" JSONB NOT NULL
);
