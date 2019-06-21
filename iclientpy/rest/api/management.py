from typing import Dict, List
from ..decorator import post, get, put, delete, head
from .model import PostWorkspaceParameter, GetWorkspaceResultItem, PostWorkspaceResultItem, MethodResult, \
    PostTileJobsItem, PostTileJobsResultItem, GetTileJobResultItem, BuildState, \
    PostTilesetUpdateJobs, PostTilesetUpdateJobsResultItem, GetTilesetExportJobResultItem, MngServiceInfo, \
    GetFileUploadResult, PostFileUploadTasksParam, PostUploadTasksResult, PostFileUploadTaskResult, \
    GetFileUploadTaskResult, RestMngFileListItem, DataStoreSetting, RestMngTileStorageInfo, UserEntity, UserInfo, \
    RoleEntity, ServiceInstance, PostAuthorizeEntity
from .abstracttypefields import mng_service_info_deserializer
from io import FileIO


class Management:
    @post('/manager/workspaces', entityKW='param')
    def post_workspaces(self, param: PostWorkspaceParameter) -> List[PostWorkspaceResultItem]:
        pass

    @get('/manager/workspaces')
    def get_workspaces(self) -> List[GetWorkspaceResultItem]:
        pass

    @delete('/manager/services/{name}')
    def delete_mapcomponent(self, name: str) -> MethodResult:
        pass

    @post('/manager/tileservice/jobs', entityKW='entity')
    def post_tilejobs(self, entity: PostTileJobsItem) -> PostTileJobsResultItem:
        pass

    @get('/manager/tileservice/jobs')
    def get_tilejobs(self) -> List[GetTileJobResultItem]:
        pass

    @head('/manager/tileservice/jobs')
    def head_tilejobs(self) -> int:
        pass

    @get('/manager/tileservice/jobs/{id}')
    def get_tilejob(self, id: str) -> GetTileJobResultItem:
        pass

    @put('/manager/tileservice/jobs/{id}', entityKW='entity')
    def put_tilejob(self, id: str, entity: BuildState) -> MethodResult:
        pass

    @delete('/manager/tileservice/jobs/{id}')
    def delete_tilejob(self, id: str) -> MethodResult:
        pass

    @head('/manager/tileservice/jobs/{id}')
    def head_tilejob(self, id: str) -> int:
        pass

    @post('/manager/tilesetupdatejobs', entityKW='entity')
    def post_tilesetupdatejobs(self, entity: PostTilesetUpdateJobs) -> PostTilesetUpdateJobsResultItem:
        pass

    @get('/manager/tilesetupdatejobs')
    def get_tilesetupdatejobs(self) -> List[GetTilesetExportJobResultItem]:
        pass

    @get('/manager/tilesetupdatejobs/{id}')
    def get_tilesetupdatejob(self, id: str) -> GetTilesetExportJobResultItem:
        pass

    @get('/manager/services/{service_name}', json_deserializer=mng_service_info_deserializer)
    def get_service(self, service_name: str) -> MngServiceInfo:
        pass

    @get('/manager/filemanager', fixed_queryKWs={'path': './', 'mode': 'editRelativePath'})
    def get_home_path(self) -> Dict[str, str]:
        pass

    @get('/manager/filemanager/uploadtasks')
    def get_fileuploadtasks(self) -> List[GetFileUploadResult]:
        pass

    @post('/manager/filemanager/uploadtasks', entityKW='entity')
    def post_fileuploadtasks(self, entity: PostFileUploadTasksParam) -> PostUploadTasksResult:
        pass

    @post('/manager/filemanager/uploadtasks/{id}', queryKWs=['toFile', 'overwrite', 'unzip'], fileKW='file')
    def post_fileuploadtask(self, id: str, file: FileIO, toFile: str, overwrite: bool = False,
                            unzip: bool = False) -> PostFileUploadTaskResult:
        pass

    @get('/manager/filemanager/uploadtasks/{id}')
    def get_fileuploadtask(self, id: str) -> GetFileUploadTaskResult:
        pass

    @get('/manager/filemanager/list', queryKWs=['path'])
    def get_file_list(self, path: str, filters: str) -> List[RestMngFileListItem]:
        pass

    @get('/manager/datastores')
    def get_datastores(self) -> List[DataStoreSetting]:
        pass

    @get('/manager/datastores/{id}')
    def get_datastore(self, id: str) -> RestMngTileStorageInfo:
        pass

    @get('/manager/security/users')
    def get_users(self) -> List[List[str]]:
        pass

    @post('/manager/security/users', entityKW='entity')
    def post_users(self, entity: UserEntity) -> MethodResult:
        pass

    @put('/manager/security/users', entityKW='entity')
    def put_users(self, entity: List[str]) -> MethodResult:
        pass

    @get('/manager/security/users/{username}')
    def get_user(self, username: str) -> UserInfo:
        pass

    @put('/manager/security/users/{username}', entityKW='entity')
    def put_user(self, username: str, entity: UserEntity) -> MethodResult:
        pass

    @delete('/manager/security/users/{username}')
    def delete_user(self, username: str) -> MethodResult:
        pass

    @get('/manager/security/roles')
    def get_roles(self) -> List[RoleEntity]:
        pass

    @post('/manager/security/roles', entityKW='entity')
    def post_roles(self, entity: RoleEntity) -> MethodResult:
        pass

    @put('/manager/security/roles', entityKW='entity')
    def put_roles(self, entity: List[str]) -> MethodResult:
        pass

    @get('/manager/security/roles/{role}')
    def get_role(self, role: str) -> RoleEntity:
        pass

    @put('/manager/security/roles/{role}', entityKW='entity')
    def put_role(self, role: str, entity: RoleEntity) -> MethodResult:
        pass

    @delete('/manager/security/roles/{role}')
    def delete_role(self, role: str) -> MethodResult:
        pass

    @get('/manager/instances')
    def get_instances(self) -> List[ServiceInstance]:
        pass

    @get('/manager/instances/{instance}')
    def get_instance(self, instance: str) -> ServiceInstance:
        pass

    @post('/manager/instances/authorize', entityKW='entity')
    def post_authorize(self, entity: PostAuthorizeEntity) -> MethodResult:
        pass
