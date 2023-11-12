from models.cloud_init.metadata import MetaData

def get_default_metadata() -> MetaData:
    return MetaData(
        instance_id='debby',
        local_hostname='debby',
    )
