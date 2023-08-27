from fastapi import FastAPI
from database import init_database

from routers_init import init_routers
from internal.cron_handler import CronHandler
from data.db.models import CronJobModel
from data.pydantic.models import CronJob
from config import SCHEDULER_USER


app = FastAPI()

init_database(app=app)

init_routers(app=app)


@app.on_event('startup')
async def init_cron_jobs():
    cron_jobs = await CronJobModel.all()
    cron_handler = CronHandler(
        user=SCHEDULER_USER
    )
    for cron_job in cron_jobs:
        cron_job_object = CronJob.instance_from_tortoise_model(cron_job)
        if not cron_handler.job_exists(
                job_id=cron_job.id
        ):
            cron_job_object.generate_full_command()
            cron_handler.add_job(
                cron_job=cron_job_object
            )
