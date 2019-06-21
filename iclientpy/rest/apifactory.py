import os
import argparse
import inspect
import sys
from enum import Enum
import requests
from requests.auth import AuthBase
import json
from typing import Callable
from functools import partial
from .api.management import Management
from .api.restdata import DataService
from .api.restmap import MapService
from .api.securityservice import SecurityService
from .api.distributedanalyst import DistributedAnalyst
from .decorator import HttpMethod, REST
from .proxyfactory import RestInvocationHandler
from .proxyfactory import create
from ..dtojson import to_json_str
from .api.datacatalog import Datacatalog
from .api.datasservice import DatasService
from .api.mapsservice import MapsService
from .api.groupsservice import GroupsService
from .api.mydepartments import MyDepartments
from .api.servicespage import ServicesPage
from .api.onlinemapsservice import OnlineMapsService
from .api.onlinedatasservice import OnlineDatasService
from .api.node_service import NodeService
from .api.securitymanagement import SecurityManagement, PortalSecurityManagement

default_session_cookie_name = 'JSESSIONID'


class CookieAuth(AuthBase):
    """
    CookieAuth是身份认证的基础类，用于记录身份认证请求头Cookie中包含的key,value

    """

    def __init__(self, cookie_value: str, cookie_name: str = default_session_cookie_name):
        """
        初始化方法

        Args:
            cookie_value:cookie头中存放key=value中的value值
            cookie_name:cookie头中存放key=value中的key值

        """
        self._value = cookie_value
        self._name = cookie_name

    def __call__(self, r: requests.PreparedRequest):
        r.prepare_cookies({self._name: self._value})
        return r


class TokenAuth(AuthBase):
    """
    基于Token认证
    """

    def __init__(self, token: str):
        """
        初始化方法

        Args:
            token: token值
        """
        self._token = token

    def __call__(self, r: requests.PreparedRequest):
        r.prepare_url(r.url, {'token': self._token})
        return r


class RestInvocationHandlerImpl(RestInvocationHandler):
    """
    rest请求的拦截器，拦截请求，并处理请求
    """

    def __init__(self, base_url: str, auth: AuthBase = None, proxies=None):

        """

        Args:
            base_url: 服务的基础地址
            auth: 存放身份验证的类
            proxies: 设置代理
        """
        self._base_url = base_url
        self._auth = auth
        self._proxies = proxies if proxies is not None else {}

    def _get_query_params(self, kwarges, queryKWs):
        """
        根据queryKWs中的查询字符串的值，从kwages中查找对应的value值，构成查询字符串的key,value的字典

        Args:
            kwarges: 所有参数的key,value集合
            queryKWs: 所有查询字符串的值

        Returns:
            存放查询字符串key和value的字典
        """
        query_params = {}
        if queryKWs:
            for name in queryKWs:
                if name in kwarges and not kwarges[name] is None:
                    if type(kwarges[name]) in (int, str, bool, float):
                        query_params[name] = kwarges[name]
                    elif isinstance(kwarges[name], Enum):
                        query_params[name] = kwarges[name].value
                    else:
                        query_params[name] = to_json_str(kwarges[name])
        return query_params

    def _send_request(self, rest: REST, *args, **kwargs):
        """
        发送请求的最终方法

        Args:
            rest: 拦截下来的rest请求存放的信息
            *args: 可变参数中的位置参数，存放请求的信息，通常根据位置进行匹配
            **kwargs: 可变参数中的字典参数，存放请求信息，根据类型进行匹配

        Returns:
            根据实际请求的类，获取返回结果类型，将请求中响应体转换为Python对象

        """
        requests_methods = {
            HttpMethod.POST: requests.post,
            HttpMethod.GET: requests.get,
            HttpMethod.PUT: requests.put,
            HttpMethod.DELETE: requests.delete
        }
        headers = {'Content-Type': 'application/json'}
        if 'files' in kwargs and kwargs['files']:
            headers = {}
        response = requests_methods[rest.get_method()](*args, **kwargs, headers=headers)
        response.raise_for_status()
        text = response.text
        result = rest.get_json_deserializer()(text)
        from json.decoder import JSONDecodeError
        try:
            json_dict = json.loads(text)
            html = json.dumps(json_dict, indent=2, sort_keys=True).replace(' ', '&nbsp;')
            setattr(result, '_repr_html_', partial(html.replace, '\n', '<br/>'))
        except AttributeError:
            pass
        except JSONDecodeError:
            pass
        return result

    def get(self, rest, uri, args, kwargs):
        """
        处理get请求

        Args:
            rest: 封装了实际请求的相关信息
            uri: 请求的发送地址
            args: 请求的位置参数
            kwargs: 请求的字典参数

        Returns:
            根据实际方法的返回类型，将get请求的响应体转换为对应的Python对象
        """
        url = self._base_url + uri + '.json' if rest.get_splice_url() else uri + '.json'
        params = self._get_query_params(kwargs, rest.get_queryKWs())
        params.update(rest.get_fixed_queryKWs())
        return self._send_request(rest, url, params=params, proxies=self._proxies, auth=self._auth)

    def post(self, rest, uri, args, kwargs):
        """
        处理post请求

        Args:
            rest: 封装了实际请求的相关信息
            uri: 请求的发送地址
            args: 请求的位置参数
            kwargs: 请求的字典参数

        Returns:
              根据实际方法的返回类型，将post请求的响应体转换为对应的Python对象
        """
        url = self._base_url + uri + '.json' if rest.get_splice_url() else uri + '.json'
        files = {rest.get_fileKW(): kwargs[rest.get_fileKW()]} if rest.get_fileKW() is not None else {}
        data = to_json_str(kwargs[rest.get_entityKW()]) if rest.get_entityKW() is not None else {}
        params = self._get_query_params(kwargs, rest.get_queryKWs())
        params.update(rest.get_fixed_queryKWs())
        result = self._send_request(rest, url, data=data, params=params, proxies=self._proxies, auth=self._auth,
                                    files=files)
        return result

    def put(self, rest, uri, args, kwargs):
        """

        处理put请求

       Args:
           rest: 封装了实际请求的相关信息
           uri: 请求的发送地址
           args: 请求的位置参数
           kwargs: 请求的字典参数

       Returns:
             根据实际方法的返回类型，将put请求的响应体转换为对应的Python对象
        """
        url = self._base_url + uri + '.json' if rest.get_splice_url() else uri + '.json'
        params = self._get_query_params(kwargs, rest.get_queryKWs())
        params.update(rest.get_fixed_queryKWs())
        return self._send_request(rest, url, data=to_json_str(kwargs[rest.get_entityKW()]), params=params,
                                  proxies=self._proxies, auth=self._auth)

    def delete(self, rest, uri, args, kwargs):
        """
        处理delete请求

       Args:
           rest: 封装了实际请求的相关信息
           uri: 请求的发送地址
           args: 请求的位置参数
           kwargs: 请求的字典参数

       Returns:
             根据实际方法的返回类型，将delete请求的响应体转换为对应的Python对象
        """
        url = self._base_url + uri + '.json' if rest.get_splice_url() else uri + '.json'
        params = self._get_query_params(kwargs, rest.get_queryKWs())
        params.update(rest.get_fixed_queryKWs())
        return self._send_request(rest, url, params=params, proxies=self._proxies, auth=self._auth)

    def head(self, rest, uri, args, kwargs):
        """
        处理head请求

       Args:
           rest: 封装了实际请求的相关信息
           uri: 请求的发送地址
           args: 请求的位置参数
           kwargs: 请求的字典参数

       Returns:
            返回head请求的状态码
        """
        url = self._base_url + uri + '.json' if rest.get_splice_url() else uri + '.json'
        params = self._get_query_params(kwargs, rest.get_queryKWs())
        params.update(rest.get_fixed_queryKWs())
        response = requests.head(url, params=params, proxies=self._proxies, auth=self._auth)
        response.raise_for_status()
        return response.status_code

    def handle_rest_invocation(self, rest, args, kwargs: dict):
        """

        Args:
            rest: 封装了实际请求的相关信息
            args: 请求的位置参数
            kwargs: 请求的字典参数

        Returns:
            根据实际方法的返回类型，将请求的响应体转换为对应的Python对象
        """
        methods = {
            HttpMethod.POST: self.post,
            HttpMethod.GET: self.get,
            HttpMethod.PUT: self.put,
            HttpMethod.DELETE: self.delete,
            HttpMethod.HEAD: self.head
        }
        uri = rest.get_uri()  # type:str
        argspec = inspect.getfullargspec(rest.get_original_func())
        kwargs = kwargs.copy()
        names = argspec[0]
        for index in range(len(args)):
            kwargs[names[index + 1]] = args[index]
        uri = uri.format(**kwargs)
        return methods[rest.get_method()](rest, uri, args, kwargs)


def _default_check_login_status(response):
    result = json.loads(response.content)
    if result['succeed'] == False:
        raise Exception('登录失败，请确保用户名和密码输入正确')


def create_auth(login_url: str, username: str, passwd: str, token: str, proxies=None,
                check: Callable = _default_check_login_status) -> AuthBase:
    """
    登录服务，并将记录登录信息的CookieAuth/TokenAuth返回，用于授权需要访问权限的api

    Args:
        login_url: 服务地址
        username: 登录的用户名
        passwd: 登录的密码
        token: 登录的token
        proxies: 设置请求的代理
        check: 检查登录状态的回调函数

    Returns:
        返回CookieAuth/TokenAuth，存放登录信息
    """
    if username is not None and passwd is not None:
        # TODO iPortal和online，iServer CAS登录后续考虑
        # TODO session超时处理，定时刷新保证不超时，以及超时检测重新登录
        response = requests.post(login_url, json={'username': username, 'password': passwd}, proxies=proxies)
        response.raise_for_status()
        if check:
            check(response)
        value = response.cookies[default_session_cookie_name]
        return CookieAuth(value)

    elif token is not None:
        return TokenAuth(token)


def _get_proxy_from_arguments():
    """
    从命令行中获取设置的代理服务地址

    Args:

    Returns:
        返回设置代理后的代理的字典
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--iclientpy-rest-proxy', dest='proxy', nargs='?')
    argv_dict = parser.parse_known_args(sys.argv)[0]
    return {} if 'proxy' not in argv_dict else {'http': argv_dict.proxy, 'https': argv_dict.proxy}


class APIFactory:
    """

    服务api的工厂类，生产服务的api

    """

    def __init__(self, base_url: str, username: str = None, passwd: str = None, token: str = None, proxies=None):
        """

        Args:
            base_url: 服务的地址
            username: 服务需要登录的用户名
            passwd: 服务需要登录的密码
            token: 服务可以访问的token
            proxies: 设置代理服务器地址
        """
        self._base_url = base_url if not base_url.endswith('/') else base_url[:-1]
        self._services_url = self._base_url + '/services'
        self._proxies = proxies if proxies is not None else _get_proxy_from_arguments()
        auth = create_auth(self._base_url + '/services/security/login.json', username, passwd, token,
                           proxies=self._proxies)
        self._handler = RestInvocationHandlerImpl(self._base_url, auth, proxies=self._proxies)

    def management(self) -> Management:
        """
        iServer管理类的api

        Returns:
            返回iServer服务管理类的api
        """
        return create(Management, self._handler)

    def security_management(self) -> SecurityManagement:
        """
        iServer安全的api

        Returns:
            返回iServer安全的api
        """
        return create(SecurityManagement, self._handler)

    def data_service(self, service_name: str) -> DataService:
        """
        返回指定服务的相关数据的api

        Args:
            service_name: 服务名称

        Returns:
            返回iServer指定服务的api
        """
        handler = RestInvocationHandlerImpl(self._services_url + '/' + service_name, proxies=self._proxies)
        return create(DataService, handler)

    def map_service(self, service_name: str) -> MapService:
        """
        返回指定地图服务的相关数据的api

        Args:
            service_name: 服务名称

        Returns:
            返回iServer指定服务的api
        """
        return create(MapService,
                      RestInvocationHandlerImpl(self._services_url + '/' + service_name, proxies=self._proxies))

    def security_service(self) -> SecurityService:
        """
        返回安全类服务的api

        Returns:
            返回iServer安全相关的api
        """
        return create(SecurityService, RestInvocationHandlerImpl(self._services_url, proxies=self._proxies))

    def distributedanalyst_service(self, service_name: str = 'distributedanalyst/rest',
                                   version: str = 'v1') -> DistributedAnalyst:
        """
        返回分布式分析服务的api

        Args:
            service_name:服务名称，默认为distributedanalyst/rest
            version:版本，默认为v1

        Returns:
            返回iServer分布式分析相关api
        """
        return create(DistributedAnalyst,
                      RestInvocationHandlerImpl(self._services_url + '/' + service_name + '/' + version + '/jobs',
                                                proxies=self._proxies))

    def datacatalog_service(self, service_name: str = 'datacatalog/rest') -> Datacatalog:
        """
        返回数据目录服务api

        Args:
            service_name:服务名称，默认为datacatalog/rest

        Returns:
            返回iServer数据目录服务api
        """
        return create(Datacatalog,
                      RestInvocationHandlerImpl(self._services_url + '/' + service_name, proxies=self._proxies))

    def servicespage(self):
        return create(ServicesPage,
                      RestInvocationHandlerImpl(self._base_url, proxies=self._proxies))


class iPortalAPIFactory:
    def __init__(self, base_url: str, username: str = None, passwd: str = None, token: str = None, proxies=None):
        """

        Args:
            base_url: 服务的地址
            username: 服务需要登录的用户名
            passwd: 服务需要登录的密码
            token: 服务可以访问的token
            proxies: 设置代理服务器地址

        """
        self._base_url = base_url if not base_url.endswith('/') else base_url[:-1]
        self._proxies = proxies if proxies is not None else _get_proxy_from_arguments()
        auth = create_auth(self._base_url + '/web/login.json', username, passwd, token, proxies=self._proxies)
        self._handler = RestInvocationHandlerImpl(self._base_url, auth, proxies=self._proxies)

    def datas_service(self) -> DatasService:
        """
        获取iPortal MyDatas服务

        Returns:
            iPortal MyDatas服务
        """
        return create(DatasService, self._handler)

    def maps_service(self) -> MapsService:
        """
        获取iPortal Maps服务

        Returns:
            iPortal Maps服务
        """
        return create(MapsService, self._handler)

    def groups_service(self) -> GroupsService:
        """
        获取iPortal Groups群组服务

        Returns:
            iPortal Groups群组服务
        """
        return create(GroupsService, self._handler)

    def mydepartments_service(self) -> MyDepartments:
        """
        获取iPortal MyDepartments服务

        Returns:
            iPortal MyDepartments服务
        """
        return create(MyDepartments, self._handler)

    def security_management(self) -> PortalSecurityManagement:
        """
        获取iPortal安全的api

        Returns:
            返回iPortal安全的api
        """
        return create(PortalSecurityManagement, self._handler)


class iManagerAPIFactory:
    def __init__(self, base_url: str, username: str = None, passwd: str = None, token: str = None, proxies=None):
        """

        Args:
            base_url: 服务的地址
            username: 服务需要登录的用户名
            passwd: 服务需要登录的密码
            token: 服务可以访问的token
            proxies: 设置代理服务器地址

        """
        self._base_url = base_url
        self._proxies = proxies if proxies is not None else _get_proxy_from_arguments()

        def _check_imanager_login_status(response):
            if response.status_code == 600:
                raise Exception('登录失败，请确保用户名和密码输入正确')

        auth = create_auth(self._base_url + '/security/tokens.json', username, passwd, token, proxies=self._proxies,
                           check=_check_imanager_login_status)
        self._handler = RestInvocationHandlerImpl(self._base_url, auth, proxies=self._proxies)

    def node_service(self):
        """
        获取iManager 节点服务

        Returns:
            iManager 节点服务
        """
        return create(NodeService, self._handler)


def create_sso_auth(url: str, username: str, passwd: str, token: str, proxies=None) -> AuthBase:
    if username is not None and passwd is not None:
        SSO_URL = 'https://sso.supermap.com/login'
        params = {'format': 'json'}
        params.update({'service': url})
        session = requests.session()
        lt_res = session.get(SSO_URL, params=params, proxies=proxies, allow_redirects=False)
        params.update(json.loads(lt_res.content))
        params.update({"username": username, "password": passwd})
        ticket_res = session.post(SSO_URL, params=params, proxies=proxies, allow_redirects=False)
        if ticket_res.status_code != 302:
            raise Exception("登录失败，请确保用户名和密码输入正确")
        url = ticket_res.headers["location"]
        online_res = session.get(url, proxies=proxies, allow_redirects=False)
        online_jsessionid = online_res.cookies[default_session_cookie_name]
        return CookieAuth(online_jsessionid)


class OnlineAPIFactory:
    def __init__(self, base_url: str = None, username: str = None, passwd: str = None, token: str = None, proxies=None):
        """

        Args:
            username: 服务需要登录的用户名
            passwd: 服务需要登录的密码
            token: 服务可以访问的token
            proxies: 设置代理服务器地址
        """
        self._base_url = base_url + 'web' if base_url.endswith('/') else base_url + '/web'
        self._proxies = proxies if proxies is not None else _get_proxy_from_arguments()
        auth = create_sso_auth(self._base_url + 'shiro-cas' if base_url.endswith('/') else base_url + '/shiro-cas',
                               username, passwd, token, proxies=self._proxies)
        self._handler = RestInvocationHandlerImpl(self._base_url, auth, proxies=self._proxies)

    def datas_service(self) -> OnlineDatasService:
        """
        获取Online数据服务

        Returns:
            Online数据服务
        """
        return create(OnlineDatasService, self._handler)

    def maps_service(self) -> OnlineMapsService:
        """
        获取Online地图服务

        Returns:
            Online地图服务
        """
        return create(OnlineMapsService, self._handler)
