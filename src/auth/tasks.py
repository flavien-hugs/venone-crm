from src import scheduler


@scheduler.task('interval', id='do_job_one', seconds=30, misfire_grace_time=900)
def get_user():
    print('job 1 executed')
