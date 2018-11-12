_endpoints = []
_additional_repositories = {}
version = '0.3.3dev'

def add_endpoints(*endpoints):
    global _endpoints
    _endpoints.extend(endpoints)

def get_endpoints():
    global _endpoints
    return _endpoints

def add_repositories(*args, **kwargs):
    global _additional_repositories
    for arg in args:
        _additional_repositories.update(arg)
        _additional_repositories.update(kwargs)

def get_repositories():
    global _additional_repositories
    return _additional_repositories