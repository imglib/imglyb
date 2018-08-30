import jnius_config

additional_endpoints = []
additional_repositories = {}

def add_endpoints(*endpoints):
    global additional_endpoints
    additional_endpoints.extend(endpoints)

def get_endpoints():
    global additional_endpoints
    return additional_endpoints

def add_repositories(*args, **kwargs):
    global additional_repositories
    for arg in args:
        additional_repositories.update(arg)
    additional_repositories.update(kwargs)

def get_repositories():
    global additional_repositories
    return additional_repositories