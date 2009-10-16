from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.datastore import entity_pb


def serialize_models(models):
	if models is None:
		return None
	elif isinstance(models, db.Model):
		# Just one instance
		return db.model_to_protobuf(models).Encode()
	else:
		# A list
		return [db.model_to_protobuf(x).Encode() for x in models]

def deserialize_models(data):
	if data is None:
		return None
	elif isinstance(data, str):
		# Just one instance
		return db.model_from_protobuf(entity_pb.EntityProto(data))
	else:
		return [db.model_from_protobuf(entity_pb.EntityProto(x)) for x in data]


def get_cached_by_key_name(cls, key_names):
	"""Gets multiple entitites by key name using memcache if available, and 
	returns a dict key_name:entity.
	"""
	key_names = set(key_names)

	# Get all gadget Protocol Buffers from memcache.
	namespace = cls.__name__
	pbs = memcache.get_multi(key_names, namespace=namespace)
	found = [key_name for key_name in key_names if key_name in pbs]

	# Build a dict with the deserialized entities.
	res = dict(zip(found, deserialize_models(pbs[key_name] for key_name in \
		found)))

	if len(key_names) != len(found):
		# Get a list of those not found in memcache, and fetch them.
		not_found = [key_name for key_name in key_names if key_name not in \
			pbs]
		entities = cls.get_by_key_name(not_found)
		values = [entity for entity in entities if entity]

		if values:
			keys = [key_name for key_name, entity in zip(not_found, 
				entities) if entity]

			# Serialize and store the fetched entities in memcache.
			memcache.set_multi(dict(zip(keys,
				serialize_models(values))), namespace=namespace)

			res.update(dict(zip(keys, values)))
			
	return res
