import jnius_config

additional_endpoints = []

def add_endpoints(*endpoints):
    global additional_endpoints
    additional_endpoints.extend(endpoints)

def get_endpoints():
    global additional_endpoints
    return additional_endpoints