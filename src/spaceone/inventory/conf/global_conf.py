DATABASE_AUTO_CREATE_INDEX = True
DATABASES = {
    'default': {
        'db': 'inventory',
        'host': 'localhost',
        'port': 27017,
        'username': 'admin',
        'password': 'password',
        'read_preference': 'SECONDARY_PREFERRED'
    }
}

CACHES = {
    'default': {
        'backend': 'spaceone.core.cache.redis.RedisCache',
        'db': 0,
        'encoding': 'utf-8',
        'host': 'localhost',
        'port': 6379,
        'socket_timeout': 10,
        'socket_connect_timeout': 10

    },
    # 'local': {
    #     'backend': 'spaceone.core.cache.local_cache.LocalCache',
    #     'max_size': 128,
    #     'ttl': 300
    # }
}

# Garbage Collection Policies
JOB_TIMEOUT = 2  # 2 Hours
JOB_TERMINATION_TIME = 2 * 30  # 2 Months
RESOURCE_TERMINATION_TIME = 6 * 30  # 6 Months
DEFAULT_DELETE_POLICIES = {
    'inventory.CloudService': 48,  # 48 Hours
    'inventory.CloudServiceType': 48,  # 48 Hours
    'inventory.Region': 48,  # 48 Hours
}
DEFAULT_DISCONNECTED_STATE_DELETE_POLICY = 3  # 3 Count
DELETE_EXCLUDE_DOMAINS = []

HANDLERS = {
}

CONNECTORS = {
    'CollectorPluginConnector': {
        'endpoint': 'grpc://localhost:65533'
    },
    'SpaceConnector': {
        'backend': 'spaceone.core.connector.space_connector.SpaceConnector',
        'endpoints': {
            'identity': 'grpc://localhost:50051',
            'plugin': 'grpc://localhost:50053',
            'repository': 'grpc://localhost:50054',
            'secret': 'grpc://localhost:50055',
            'config': 'grpc://localhost:50057',
        }
    },
}

ENDPOINTS = {}
LOG = {}
QUEUES = {
    'finops_q': {
        'backend': 'spaceone.core.queue.redis_queue.RedisQueue',
        'channel': 'inventory_opt_job',
        'host': 'localhost',
        'port': 6379
    },
}
SCHEDULERS = {
    'inventory_opt_scheduler': {
        "backend": "spaceone.inventory.scheduler.inventory_scheduler.InventoryHourlyScheduler",
        'interval': 1,
        'minute': ':21',
        'queue': 'finops_q'
    }
}
WORKERS = {
    'inventory_opt_worker': {
        'backend': 'spaceone.core.scheduler.worker.BaseWorker',
        'pool': 1,
        'queue': 'finops_q'
    },
}
TOKEN = ""
TOKEN_INFO = {
    'config': {
        'host': 'localhost'
    },
    'protocol': 'consul',
    'uri': 'root/api_key/TOKEN'
}
collect_queue = "finops_q"  # Queue name for asynchronous collect