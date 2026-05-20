from django.db.models import PositiveIntegerField


class TaskRelativeIdField(PositiveIntegerField):
    def pre_save(self, model_instance, add) -> int:
        if not add:
            return getattr(model_instance, self.attname)
        values = self.model.objects.filter(task_id=model_instance.task_id).values_list(
            self.attname, flat=True
        ) or (0,)
        value = max(values) + 1
        return value
