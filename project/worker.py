from celery import Celery

app = Celery("project")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.task_routes = {
    "project.custom_user.tasks.send_push_notification": {
        "queue": "push_notifications",
    },
    "project.gig.tasks.create_gig_thumbnail": {
        "queue": "thumbnails",
    },
}
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
