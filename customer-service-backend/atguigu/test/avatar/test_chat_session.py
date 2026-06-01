
# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
import os
import sys
import json

from typing import List

from alibabacloud_lingmou20250527.client import Client as LingMou20250527Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_lingmou20250527 import models as ling_mou_20250527_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient


class Sample:
    def __init__(self):
        pass

    @staticmethod
    def create_client() -> LingMou20250527Client:
        """
        使用凭据初始化账号Client
        @return: Client
        @throws Exception
        """
        # 工程代码建议使用更安全的无AK方式，凭据配置方式请参见：https://help.aliyun.com/document_detail/378659.html。
        credential = CredentialClient()
        config = open_api_models.Config(
            credential=credential
        )
        # Endpoint 请参考 https://api.aliyun.com/product/LingMou
        config.endpoint = f'lingmou.cn-beijing.aliyuncs.com'
        return LingMou20250527Client(config)

    @staticmethod
    def main(
        args: List[str],
    ) -> None:
        client = Sample.create_client()
        create_chat_session_request = ling_mou_20250527_models.CreateChatSessionRequest(
            instance_id='avatar_2dchat_public_cn-9yo4t2pw501'
        )
        runtime = util_models.RuntimeOptions()
        headers = {}
        try:
            resp = client.create_chat_session_with_options('C1rRS1KmS3WurHor8HXYlSkQ', create_chat_session_request, headers, runtime)
            print(json.dumps(resp, default=str, indent=2))
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))

    @staticmethod
    async def main_async(
        args: List[str],
    ) -> None:
        client = Sample.create_client()
        create_chat_session_request = ling_mou_20250527_models.CreateChatSessionRequest(
            instance_id='avatar_2dchat_public_cn-9yo4t2pw501'
        )
        runtime = util_models.RuntimeOptions()
        headers = {}
        try:
            resp = await client.create_chat_session_with_options_async('C1rRS1KmS3WurHor8HXYlSkQ', create_chat_session_request, headers, runtime)
            print(json.dumps(resp, default=str, indent=2))
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))


if __name__ == '__main__':
    Sample.main(sys.argv[1:])
