from django.contrib.contenttypes.models import ContentType


def get_task_keys(id: int, ct_id: int, end: bool = False, delete: bool = False) -> dict:
    keys = {"key": f"task:{id}:{ct_id}"}
    if not delete:
        keys.update({"lock_key": f"{id}:{ct_id}:{end}"})
    else:
        keys.update({"lock_key": f"delete:{id}:{ct_id}"})
    return


def get_delete_by_object(object):
    ct = ContentType.objects.get_for_model(object)
    ct_id = ct.id
    id = object.id
    return get_task_keys(id, ct_id, delete=True)
