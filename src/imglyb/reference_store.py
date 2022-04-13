import threading

'''

'''
class ReferenceStore(object):

    def __init__(self):
        self.lock    = threading.RLock()
        self.store   = dict()
        self.next_id = 0

    def add_reference(self, ref_id, reference):
        with self.lock:
            self.store[ref_id] = reference

    def add_reference_with_new_id(self, reference):
        ref_id = self.get_next_id()
        self.add_reference(ref_id, reference)
        return ref_id

    def get_next_id(self):
        with self.lock:
            next_id = self.next_id
            self.next_id += 1
        return next_id

    def remove_reference(self, ref_id):
        with self.lock:
            if ref_id in self.store:
                del self.store[ref_id]

    def clear(self):
        with self.lock:
            self.store.clear()

    def reset_next_id(self):
        with self.lock:
            self.next_id = 0

    def number_of_stored_references(self):
        return len(self.store)
