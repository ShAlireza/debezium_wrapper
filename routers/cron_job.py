from typing import List

from fastapi import APIRouter, Depends, Body, Path, status, Response


from internal import CronHandler
from data import CronJob, CronJobPost, CronJobResponse, CronJobPatch
from data.db.models import CronJobModel, KafkaConnectModel

from config import SCHEDULER_USER

router = APIRouter()

__all__ = ('router',)


async def get_cron_handler():
    return CronHandler(
        user=SCHEDULER_USER
    )


@router.post("/", response_model=CronJobResponse)
async def add_job(
        response: Response,
        cron_handler: CronHandler = Depends(get_cron_handler),
        job: CronJobPost = Body(
            ...,
            title='Job to be added to scheduling service'
        )
):
    await KafkaConnectModel.get(
        host=job.host,
        port=job.port
    )

    cron_job = CronJob(**job.dict())
    cron_job.generate_full_command()

    cron_job_model = await CronJobModel.create(**cron_job.dict())

    cron_job.id = cron_job_model.id

    cron_handler.add_job(
        cron_job=cron_job
    )

    return cron_job_model


@router.get("/", response_model=List[CronJobResponse])
async def get_jobs(
):

    jobs = await CronJobModel.all()

    return jobs


@router.get("/{job_id}", response_model=CronJobResponse)
async def get_job(
        job_id: str = Path(..., title='Job id to retrieve')
):
    job = await CronJobModel.get(
        id=job_id
    )

    return job


@router.patch("/{job_id}", response_model=CronJobResponse)
async def edit_job(
        cron_handler: CronHandler = Depends(get_cron_handler),
        job_id: str = Path(..., title='Job id to edit'),
        job: CronJobPatch = Body(..., title='Fields to update')
):
    update_data = job.dict(exclude_unset=True)

    cron_job = await CronJobModel.get(
        id=job_id
    )

    new_job = CronJob.instance_from_tortoise_model(cron_job)
    new_job = new_job.copy(update=update_data)
    new_job.generate_full_command()

    cron_job = await cron_job.update_from_dict(
        data=new_job.dict(exclude_unset=True)
    )
    await cron_job.save()

    cron_handler.delete_job(
        job_id=job_id
    )

    cron_handler.add_job(
        cron_job=new_job
    )

    return cron_job


@router.delete("/{job_id}", response_model=CronJobResponse,
               status_code=status.HTTP_200_OK)
async def delete_job(
        cron_handler: CronHandler = Depends(get_cron_handler),
        job_id: str = Path(..., title='Job id to delete')
):
    job = await CronJobModel.get(
        id=job_id
    )
    cron_handler.delete_job(job_id=job_id)

    await CronJobModel.filter(id=job_id).delete()

    return job
