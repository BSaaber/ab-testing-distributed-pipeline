import clickhouse_connect

def create_log_testid_data(client):
    client.command('DROP TABLE IF EXISTS log_testid_data')
    client.command('SET flatten_nested = 0')
    client.command(
"""
CREATE TABLE log_testid_data
(
    `session_id` String,
    `testid` INT,
    `datetime` String,
    `is_purchased` BOOL
)
ENGINE = MergeTree
ORDER BY session_id
"""
    )
    result = client.query('DESCRIBE TABLE log_testid_data')
    print(result.column_names)
    print(result.result_columns)


client = clickhouse_connect.get_client(host='localhost', port=8123, username='admin', password='admin')
create_log_testid_data(client)
