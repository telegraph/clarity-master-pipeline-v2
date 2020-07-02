from google.cloud import storage


class BlobComposer:
    MAX_CONCATENATION = 32

    def __init__(self, file_prefix, source_csv):
        self.file_prefix = file_prefix
        self.list_of_sources = source_csv
        self.full_file_name = f"{file_prefix}_full.csv"

    def __len__(self):
        return len(self.list_of_sources)

    @property
    def is_single_file(self):
        return len(self.list_of_sources) == 1

    @property
    def is_over_max_concatenation(self):
        return len(self.list_of_sources) > 32

    @property
    def chunks(self):
        return (
            self.list_of_sources[i:i + self.MAX_CONCATENATION]
            for i in range(0, len(self.list_of_sources), self.MAX_CONCATENATION)
        )

    @property
    def intermediary_mapping(self):
        if not self.is_over_max_concatenation:
            return []
        else:
            return [
                (
                    '{}_intermediary_{}.csv'.format(self.file_prefix, i),
                    chunk
                )
                for i, chunk in enumerate(self.chunks)
            ]


class BlobManager:

    def __init__(self, logger, transfer, operation_prefix='', reduce=True):

        extract_file_prefix = transfer.gcs.extract_file_prefix
        if len(operation_prefix):
            self.extract_file_prefix = f"{operation_prefix}_{extract_file_prefix}"
        else:
            self.extract_file_prefix = extract_file_prefix
        self.logger = logger

        storage_client = storage.Client(project=transfer.project)
        self.bucket = storage_client.get_bucket(transfer.gcs.bucket)

        self.files_to_concatenate = list(self.bucket.list_blobs(prefix=self.extract_file_prefix))

        self.reduce = reduce

    def _reduce_blob(self, blob_manager, ):

        if blob_manager.is_single_file:
            self.logger.info("BlobReducer: Single file export")
            return blob_manager.list_of_sources[0]

        elif blob_manager.is_over_max_concatenation:
            self.logger.info("BlobReducer: {} files to concatenate. Need intermediary".format(len(blob_manager)))

            blobs_for_full_file = []
            for intermediary_file_name, chunk in blob_manager.intermediary_mapping:
                intermediary_blob = self.bucket.blob(blob_name=intermediary_file_name)
                intermediary_blob.compose(chunk)
                blobs_for_full_file.append(intermediary_blob)
        else:
            blobs_for_full_file = blob_manager.list_of_sources

        self.logger.info("BlobReducer: {} intermediary files created".format(len(blobs_for_full_file)))

        full_file_blob = self.bucket.blob(blob_name=blob_manager.full_file_name)
        full_file_blob.compose(blobs_for_full_file)

        self.logger.info("BlobReducer: single file created")

        return full_file_blob

    def __enter__(self):
        if self.reduce:
            blob_manager = BlobComposer(self.extract_file_prefix, self.files_to_concatenate)
            return self._reduce_blob(blob_manager)
        else:
            return self.files_to_concatenate

    def __exit__(self, type, value, traceback):

        file_to_be_deleted = list(self.bucket.list_blobs(prefix=self.extract_file_prefix))
        self.logger.info(
            "BlobReducer: removing {} files from bucket {}".format(len(file_to_be_deleted), self.bucket.name))
        for temporary_file in file_to_be_deleted:
            self.logger.info("BlobReducer: removing {}".format(temporary_file.name))
            temporary_file.delete()

        
