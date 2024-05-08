#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import os
import json
import signal
import functools
import logging
import socket
import time
from urllib import request, error, parse
from config import read_config, save_config, check_config, cfg
from get_ip import get_ip

def header():
    h = {
        'User-Agent': 'Client/0.0.1 ({})'.format(cfg['email'])
    }
    return h

def get_record_id(domain, sub_domain):
    url = 'https://dnsapi.cn/Record.List'
    params = parse.urlencode({
        'login_token': cfg['login_token'],
        'format': 'json',
        'domain': domain
    })
    req = request.Request(url=url, data=params.encode('utf-8'), method='POST', headers=header())
    try:
        resp = request.urlopen(req).read().decode()
    except (error.HTTPError, error.URLError, socket.timeout):
        return None
    records = json.loads(resp).get('records', {})
    for item in records:
        if item.get('name') == sub_domain:
            return item.get('id')
    return None


def update_record():
    url = 'https://dnsapi.cn/Record.Ddns'
    params = parse.urlencode({
        'login_token': cfg['login_token'],
        'format': 'json',
        'domain': cfg['domain'],
        'sub_domain': cfg['sub_domain'],
        'record_id': cfg['record_id'],
        'record_line': '默认'
    })
    req = request.Request(url=url, data=params.encode('utf-8'), method='POST', headers=header())
    resp = request.urlopen(req).read().decode()
    records = json.loads(resp)
    if int(records['status']['code']) != 1:
        logging.info("record updated: %s" % records)
        logging.error('配置错误，无法更新dns，请检查配置文件')
        exit()
    cfg['last_update_time'] = str(time.gmtime())
    logging.info("record updated: %s" % records)


# async def main():
def main():
    while 1:
        current_ip = get_ip()
        if current_ip:
            # 对于拥有多个出口 IP 负载均衡的服务器，上面的 get_ip() 函数会在几个 ip 之间不停切换
            # 然后频繁进入这个判断，进行 update_record()，然后很快就会触发 API Limited 了
            # 于是建立一个IP池记载这个服务器的几个出口IP，以免频繁切换
            
            ip_count = int(cfg['ip_count'])
            ip_pool = cfg['ip_pool'].split(',')[:ip_count]
            cfg['current_ip'] = current_ip
            if current_ip not in ip_pool:
                # new ip found
                logging.info("new ip found: %s", current_ip)
                
                ip_pool.insert(0, current_ip)
                cfg['ip_pool'] = ','.join([str(x) for x in ip_pool[:ip_count]])
                update_record()
                save_config()
            else:
                logging.info('IP 地址无变化，跳过更新')
        else:
            logging.error('get current ip FAILED.')

        try:
            interval = int(cfg['interval'])
        except ValueError:
            interval = 10
        # await asyncio.sleep(interval)
        logging.info('更新完成，等待' + str(interval) + ' s后再次检测')
        logging.info('-' * 100)
        time.sleep(interval)


def ask_exit(_sig_name):
        logging.warning('got signal {}: exit'.format(_sig_name))
        loop.stop()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s : %(message)s')
    logging.info('*' * 100)
    logging.info('Dnspod ddns自动更新工具 V1.0')
    logging.info('原版代码： https://gitcode.com/strahe/dnspod-ddns/')
    logging.info('更新：obaby')
    logging.info('博客:https://h4ck.org.cn')
    logging.info('    https://oba.by')
    logging.info('更新内容：1）修复配置错误代码继续运行 2）输出dnspod错误提示')
    logging.info('='*100)
    logging.info('开始自动更新服务...')
    read_config()
    check_config()
    cfg['record_id'] = get_record_id(cfg['domain'], cfg['sub_domain'])
    logging.info("get record_id: %s" % str(cfg['record_id']))
    logging.info("watching ip for ddns: %s.%s" % (cfg['sub_domain'], cfg['domain']))

    loop = asyncio.get_event_loop()
    for sig_name in ('SIGINT', 'SIGTERM'):
        try:
            loop.add_signal_handler(getattr(signal, sig_name), functools.partial(ask_exit, sig_name))
        except NotImplementedError:
            pass  # 使兼容 WINDOWS
    try:
        loop.run_until_complete(main())
    except (KeyboardInterrupt, RuntimeError):
        logging.info('stop...')
    finally:
        loop.close()