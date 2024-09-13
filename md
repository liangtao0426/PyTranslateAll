1.火山翻译每个月有免费的200w个字符可以用于翻译，后每200w个字符49元
2.由于火山翻译的api服务的问题可能会有部分单元格没有翻译的情况，可以手动翻译或者等待一会从新翻译
3.使用方法：
    1.在config文件中增加修改access_key和secret_key中的值，可以自行去火山翻译官网注册（免费的）地址：https://console.volcengine.com/auth/login
    2.其他字段不需要修改
    3.然后修改input_file_path（需要翻译的文档地址）
    4.然后修改output_file_path（翻译完成后的文件名称自定义）
    5.另外如果需要其他的翻译服务可以在config文件中新增配置后修改process_excel('hs_api')中hs_api的部分