def init_routers(app):
    from routers import debezium_router, cron_job_router

    app.include_router(
        cron_job_router,
        prefix='/api/cron',
        tags=['Cron']
    )

    app.include_router(
        debezium_router,
        prefix='/api/debezium',
        tags=['Debezium']
    )
