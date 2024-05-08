### 


# dnspod-ddns


20250508更新记录：  
```
1）修复配置错误代码继续运行 
2）输出dnspod错误提示
```

原版地址：  
https://gitcode.com/strahe/dnspod-ddns/  

问题反馈：  
https://h4ck.org.cn  

定时检查 ip 变化并更新dnspod的解析记录.

程序运行在python 3.5以上.

## 开始使用

### 本地运行

在 Linux 下，配置文件路径： `/etc/dnspod/ddnsrc` (也可通过环境变量设置)

在 Windows 下，配置文件路径为本目录下的：`ddnspod.cfg`

可配置的有效参数如下:

```config
LOGIN_TOKEN=token_id,token
DOMAIN=domain.com
SUB_DOMAIN=www
INTERVAL=5
EMAIL=you@email.com
IP_COUNT=1
```

* LOGIN_TOKEN : 必填, 在dnspod上申请的api组成的token,参考：https://support.dnspod.cn/Kb/showarticle/tsid/227/
* DOMAIN : 必填, 在dnspod解析的域名
* SUB_DOMAIN : 必填, 使用ddns的子域名
* INTERVAL: 选填, 轮询检查的时间间隔, 单位秒， 默认为5, 建议不要小于5
* EMAIL: 选填, 你的邮箱
* IP_COUNT: 选填, 你服务器的出口IP数量，一般为1，填大了一般也没事（玩 OpenWrt 的可能会有多个IP）

运行 `python ddns.py`

### 测试环境

以下为测试通过的环境：
- [x] Windows 11
- [x] Windows 10
- [x] Windows Server 2016
- [x] Debian 4.9.8
- [x] Ubuntu 22.04
