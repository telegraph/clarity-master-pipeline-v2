import time

from google.cloud import bigquery


class BigQueryClient(bigquery.Client):

    def __init__(self, project, **kwargs):

        super().__init__(project, **kwargs)

    def run_query(self, query, job_config, return_results=False):
        if not job_config:
            job_config = bigquery.QueryJobConfig()

        job_config.write_disposition = 'WRITE_TRUNCATE'
        query_job = self.query(query, job_config=job_config)  # API request

        while True:
            query_job.reload()  # Refreshes the state via a GET request.
            if query_job.state == 'DONE':
                if query_job.error_result:
                    raise RuntimeError(query_job.errors)
                break
            time.sleep(1)

        if return_results:
            iterator = query_job.result()
            headers = [col.name for col in iterator.schema]

            data = []
            for row in iterator:
                result_row = []
                for point in row:
                    result_row.append(point)
                data.append(result_row)

            return {'headers': headers, 'data': data}
