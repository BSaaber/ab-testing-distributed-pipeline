
from confluent_kafka import Producer
import time
from random import random, randint
import uuid
import datetime

IN_DOCKER = True

config = {
    'bootstrap.servers': 'kafka1:9092,kafka2:9093' if IN_DOCKER else 'localhost:29092,localhost:29093',
}


def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [partition {}]'.format(msg.topic(), msg.partition()))


# NOTE:
# In this test config experiments do not overlap
# So we don't salt them

TESTID_BUTTON_SIZE_CONTROL = 100
TESTID_BUTTON_SIZE_TEST = 101
TESTIDS_BUTTON_SIZE = {
    'testids': [
        {
            'id': TESTID_BUTTON_SIZE_CONTROL,
            'batches': list(range(40, 60)),
        },
        {
            'id': TESTID_BUTTON_SIZE_TEST,
            'batches': list(range(60, 80)),
        },
    ]
}

TESTID_ICON_COLOR_CONTROL = 200
TESTID_ICON_COLOR_TEST = 201
TESTIDS_ICON_COLOR = {
    'testids': [
        {
            'id': TESTID_ICON_COLOR_CONTROL,
            'batches': list(range(0, 20)),
        },
        {
            'id': TESTID_ICON_COLOR_TEST,
            'batches': list(range(20, 40)),
        },
    ]
}


def generate_testids(testid_configs):
    testids = []

    batch = randint(0, 99)
    for testid_config in testid_configs:
        for testid in testid_config['testids']:
            if batch in testid['batches']:
                testids.append(testid['id'])

    return testids


def check_purchase(probability):
    return 1 if random() < probability else 0


def perform_user_session(user_session_testids):
    user_session_logs = []
    buy_probability = 0.3

    if TESTID_BUTTON_SIZE_TEST in user_session_testids:
        buy_probability += 0.1

    if TESTID_ICON_COLOR_TEST in user_session_testids:
        buy_probability -= 0.15

    was_bought = check_purchase(buy_probability)

    if was_bought:
        user_session_logs.append('purchase confirmed')
    else:
        user_session_logs.append('purchase aborted')

    return user_session_logs


p = Producer(config)
TESTID_CONFIGS = [TESTIDS_BUTTON_SIZE, TESTIDS_ICON_COLOR]
itr = 1
while True:
    p.poll(0)
    print('start user session n {}'.format(itr))

    # in production testid splitter should be a separate service
    testids = generate_testids(TESTID_CONFIGS)

    logs = perform_user_session(testids)
    logs = ','.join(logs)

    session_id = uuid.uuid4()

    data = {
        'session_id': str(session_id),
        'logs': logs,
        'testids': ','.join(map(str, testids)),
        'datetime': str(datetime.datetime.now())
    }

    print(data)
    p.produce(topic='test', key=str(session_id), value=str(data).encode('utf-8'), callback=delivery_report)

    time.sleep(0.001)
    itr += 1
    print('end of iteration in cycle\n\n\n')



