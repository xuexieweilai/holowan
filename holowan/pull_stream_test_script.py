# -*- coding:UTF-8 -*-
# Create your tests here.
import os
import sys
sys.path.append('/Users/yangyusong/Documents/video_code/Audio_Video_TestTools/holoWAN')
sys.path.append('/Users/yangyusong/Documents/video_code/Audio_Video_TestTools/mediatools')

import urllib.request
import json
import time
import datetime
import csv
import logging
import numpy as np
import holowan
import mediatools

#拉流地址，根据实际情况进行修改
pull_url = 'http://ws01.pull.yximgs.com/gifshow/ws_quic_test.flv?wsTime=f82c7ba2&wsSecret=f000c166c948f88fafaef52a08c9aaf9'
uin = 'yangyusong'

#拉流测试时间，单位秒
times = 1200

#holoWan ip和port、以及使用的pathid
holoWan_ip = '192.168.1.190'
holowan_port = '8080'
pathId = '9'

#网损条件
holowan_case_list = [
    #丢包场景
    {'uploadDict': {'bandwith_value_upload': "1", 'loss_r_upload': '0','delay_type_upload':1,'delay_const_upload':'0','queue_deth_upload': 300, 'queue_qdt_upload': 1},'downloadDict': {}},
    {'uploadDict': {'bandwith_value_upload': "1", 'loss_r_upload': '1','delay_type_upload':1,'delay_const_upload':'0','queue_deth_upload': 300, 'queue_qdt_upload': 1},'downloadDict': {}},
    {'uploadDict': {'bandwith_value_upload': "1", 'loss_r_upload': '2','delay_type_upload':1,'delay_const_upload':'0','queue_deth_upload': 300, 'queue_qdt_upload': 1},'downloadDict': {}},
    {'uploadDict': {'bandwith_value_upload': "1", 'loss_r_upload': '5','delay_type_upload':1,'delay_const_upload':'0','queue_deth_upload': 300, 'queue_qdt_upload': 1},'downloadDict': {}},
    {'uploadDict': {'bandwith_value_upload': "1", 'loss_r_upload': '10','delay_type_upload':1,'delay_const_upload':'0','queue_deth_upload': 300, 'queue_qdt_upload': 1},'downloadDict': {}},
    # {'uploadDict': {'bandwith_value_upload': "1", 'loss_r_upload': '20','delay_type_upload':1,'delay_const_upload':'0','queue_deth_upload': 300, 'queue_qdt_upload': 1},'downloadDict': {}},
    # {'uploadDict': {'bandwith_value_upload': "1", 'loss_r_upload': '30','delay_type_upload':1,'delay_const_upload':'0','queue_deth_upload': 300, 'queue_qdt_upload': 1},'downloadDict': {}},

    #固定延时场景
    {'uploadDict': {'bandwith_value_upload': "1", 'loss_r_upload': '0','delay_type_upload':1,'delay_const_upload':'20','queue_deth_upload': 300, 'queue_qdt_upload': 1},'downloadDict': {}},
    {'uploadDict': {'bandwith_value_upload': "1", 'loss_r_upload': '0','delay_type_upload':1,'delay_const_upload':'50','queue_deth_upload': 300, 'queue_qdt_upload': 1},'downloadDict': {}},
    {'uploadDict': {'bandwith_value_upload': "1", 'loss_r_upload': '0','delay_type_upload':1,'delay_const_upload':'100','queue_deth_upload': 300, 'queue_qdt_upload': 1},'downloadDict': {}},
    {'uploadDict': {'bandwith_value_upload': "1", 'loss_r_upload': '0','delay_type_upload':1,'delay_const_upload':'200','queue_deth_upload': 300, 'queue_qdt_upload': 1},'downloadDict': {}},

    # 延时抖动场景
    {'uploadDict': {'bandwith_value_upload': "1", 'loss_r_upload': '0','delay_type_upload':'3','delay_de_upload':'0','delay_me_upload':'10','delay_sd_upload':'3', 'queue_deth_upload': 300, 'queue_qdt_upload': 1},'downloadDict': {}},
	{'uploadDict': {'bandwith_value_upload': "1", 'loss_r_upload': '0','delay_type_upload':'3','delay_de_upload':'0','delay_me_upload':'50','delay_sd_upload':'17', 'queue_deth_upload': 300, 'queue_qdt_upload': 1},'downloadDict': {}},
	{'uploadDict': {'bandwith_value_upload': "1", 'loss_r_upload': '0','delay_type_upload':'3','delay_de_upload':'0','delay_me_upload':'100','delay_sd_upload':'33', 'queue_deth_upload': 300, 'queue_qdt_upload': 1},'downloadDict': {}},
	{'uploadDict': {'bandwith_value_upload': "1", 'loss_r_upload': '0','delay_type_upload':'3','delay_de_upload':'50','delay_me_upload':'200','delay_sd_upload':'50', 'queue_deth_upload': 300, 'queue_qdt_upload': 1},'downloadDict': {}},

    # 不同带宽场景
    {'uploadDict': {'bandwith_value_upload': "2", 'loss_r_upload': '0','delay_type_upload':1,'delay_const_upload':'0','queue_deth_upload': 300, 'queue_qdt_upload': 1},'downloadDict': {}},
    {'uploadDict': {'bandwith_value_upload': "1", 'loss_r_upload': '0','delay_type_upload':1,'delay_const_upload':'0','queue_deth_upload': 300, 'queue_qdt_upload': 1},'downloadDict': {}},
    {'uploadDict': {'bandwith_t_upload':2 ,'bandwith_value_upload': "600", 'loss_r_upload': '0','delay_type_upload':1,'delay_const_upload':'0','queue_deth_upload': 300, 'queue_qdt_upload': 1},'downloadDict': {}},  #600kbps
    {'uploadDict': {'bandwith_t_upload':2 ,'bandwith_type_upload': 2, 'bandwith_max_upload': "800", 'bandwith_min_upload':'400', 'loss_r_upload': '0','delay_type_upload':1,'delay_const_upload':'0','queue_deth_upload': 300, 'queue_qdt_upload': 1},'downloadDict': {}},  #400~800kbps 正玄波 60秒周期

    #组合场景  
    # 1Mbps + 2%丢包 + 50ms延时 
    {'uploadDict': {'bandwith_value_upload': "1", 'loss_r_upload': '2','delay_type_upload':1,'delay_const_upload':'50','queue_deth_upload': 300, 'queue_qdt_upload': 1},'downloadDict': {}},
    # 1Mbps + 2%丢包 + 50ms jitter
    {'uploadDict': {'bandwith_value_upload': "1", 'loss_r_upload': '2','delay_type_upload':'3','delay_de_upload':'0','delay_me_upload':'50','delay_sd_upload':'17', 'queue_deth_upload': 300, 'queue_qdt_upload': 1},'downloadDict': {}},

    # 1Mbps + 2%丢包 + 100ms延时 
    {'uploadDict': {'bandwith_value_upload': "1", 'loss_r_upload': '2','delay_type_upload':1,'delay_const_upload':'100','queue_deth_upload': 300, 'queue_qdt_upload': 1},'downloadDict': {}},
    # 1Mbps + 2%丢包 + 100ms jitter
    {'uploadDict': {'bandwith_value_upload': "1", 'loss_r_upload': '2','delay_type_upload':'3','delay_de_upload':'0','delay_me_upload':'100','delay_sd_upload':'33', 'queue_deth_upload': 300, 'queue_qdt_upload': 1},'downloadDict': {}},

    # 600kbps + 2%丢包 + 50ms延时 
    {'uploadDict': {'bandwith_t_upload':2 ,'bandwith_value_upload': "600", 'loss_r_upload': '2','delay_type_upload':1 ,'delay_const_upload':'50','queue_deth_upload': 300, 'queue_qdt_upload': 1},'downloadDict': {}},
    # 600kbps + 2%丢包 + 50ms jitter
    {'uploadDict': {'bandwith_t_upload':2 ,'bandwith_value_upload': "600", 'loss_r_upload': '2','delay_type_upload':'3','delay_de_upload':'0','delay_me_upload':'50','delay_sd_upload':'17', 'queue_deth_upload': 300, 'queue_qdt_upload': 1},'downloadDict': {}},

    # 400~800kbps + 2%丢包 + 50ms延时 
    {'uploadDict': {'bandwith_t_upload':2 ,'bandwith_type_upload': 2, 'bandwith_max_upload': "800",'bandwith_min_upload':'400', 'loss_r_upload': '2','delay_type_upload':1,'delay_const_upload':'50','queue_deth_upload': 300, 'queue_qdt_upload': 1},'downloadDict': {}},
    # 400~800kbps+ 2%丢包 + 50ms jitter
    {'uploadDict': {'bandwith_t_upload':2 ,'bandwith_type_upload': 2, 'bandwith_max_upload': "800", 'bandwith_min_upload':'400', 'loss_r_upload': '2','delay_type_upload':'3','delay_de_upload':'0','delay_me_upload':'50','delay_sd_upload':'17', 'queue_deth_upload': 300, 'queue_qdt_upload': 1},'downloadDict': {}},

]


################################################日志记录配置#############################################################
#存储日志到文件
currenFileName = os.path.basename(__file__).split('.')[0]
currentPath = os.path.dirname(__file__)
logger = logging.getLogger(currenFileName)

#输出到屏幕信息
logger.setLevel(logging.DEBUG)
rf_handler = logging.StreamHandler(sys.stderr)#默认是sys.stderr
rf_handler.setLevel(logging.INFO) 
rf_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] - %(message)s"))
#输出到文件信息信息
f_handler = logging.FileHandler(currentPath + '/' + currenFileName + '.log')
f_handler.setLevel(logging.DEBUG)
f_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] - %(message)s"))
 
logger.addHandler(rf_handler)
logger.addHandler(f_handler)

################################################日志记录配置#############################################################
class ResultManager:
    def __init__(self):
        #创建result目录
        currentPath = os.path.dirname(__file__)
        result_dir = currentPath + '/results/'
        if not os.path.exists(result_dir):
	        os.mkdir(result_dir)
        now = datetime.datetime.now()
        #创建result文件
        self.csv_file_name = currentPath + '/results/' + 'result_' + now.strftime('%Y%m%d%H%M%S') + '.csv'
        self.csv_file = open(self.csv_file_name, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file, dialect='excel')
    #end of method

    def __del__(self):
        self.csv_file.close()
    #end of method

    def addResult(self, result_dict, holowan_config ):
        #全部转换成str
        for key, value in result_dict.items(): 
            result_dict[key] = str(value)
        
        #写入网损条件
        row = ['holowan_upload : ' + holowan_config['upload'], '' ,'holowan_download : ' + holowan_config['download']]
        self.csv_writer.writerow(row) 

        row = ['holoWan_rx_rate','mediatools_pull_block_cnt', 'mediatools_pull_bps',  'mediatools_pull_fps', 'mediatools_pull_vqoe']
        self.csv_writer.writerow(row)

        row = [result_dict['holoWan_rx_rate'],  result_dict['mediatools_pull_block_cnt'], result_dict['mediatools_pull_bps'], result_dict['mediatools_pull_fps'], result_dict['mediatools_pull_vqoe']]
        self.csv_writer.writerow(row)

        row = ['','','','','','']
        self.csv_writer.writerow(row)
        self.csv_file.flush()
        return self.csv_file_name
    #end of method
#end of class


#初始化网损
holowan = holowan.holowan(holoWan_ip, holowan_port)

#初始化mediatools
mediatools = mediatools.mediatools()

#测试结果写文件
result_manager = ResultManager()

for holowan_case in holowan_case_list:
    #set holowan
    try:
        downloadDict = holowan_case['downloadDict']
        uploadDict = holowan_case['uploadDict']
        holowan.path_emulator_config(pathId, "PATH "+ pathId, uploadDict, downloadDict)
        holowan.save_engine_emulator_config()
        #获取当前path 概要信息，并记录，用于写入测试结果
        holowan_config = holowan.result = holowan.get_statistics_information_with_pid(pathId)

        #等待1分钟，让推流适应新配置
        logger.info('网损配置变更，等待60秒后开始统计推流数据')
        time.sleep(60)
    except Exception as e:
        logger.info('Error:  ' + str(e)) 
        break

    #创建测试任务，如果创建失败，增加一次重试的机会
    n = 1
    while(1):
        create_ret = mediatools.create_monitor_task_test(pull_url,uin)
        if 'task_id' in create_ret:
            logger.info(create_ret)
            break
        else: 
            if n > 2:
                logger.error('任务创建失败，重试2次后，仍然有问题，请检查')
                break
            else:
                logger.info(create_ret)
                logger.info('任务创建失败，10秒后重试一次') 
                n = n + 1
                time.sleep(10)   
    #用于存储测试结果
    result_dict = {}

    #从mediatools平台获取测试结果
    if 'task_id' in create_ret:
        try:
            task_id = create_ret['task_id']
            logger.info('mediatools平台任务创建成功，task_id: ' + str(task_id))

            #从网损上获取推流平均码率
            rx_rate = holowan.get_rx_rate_avg(pathId, 'upload', times)
            #获取测试结果，并计算平均码率、视频卡顿次数、平均帧率、拉流画面质量
            res = mediatools.get_live_result_test(str(task_id))
            logger.debug('本次从mediatools平台获取测试结果为: ' + str(res))

            bps = mediatools.get_avg_bps(res)
            block_cnt = mediatools.get_video_block_cnt(res)
            fps = mediatools.get_avg_fps(res)
            vqoe = mediatools.get_avg_vqoe(res)

            stop_ret = mediatools.stop_monitor_task_test(str(task_id))
            logger.info(stop_ret)

            logger.info('网损配置          ： '  + str(holowan_config))
            logger.info('推流平均码率      ： ' + str(rx_rate) + ' kbps')
            logger.info('拉流卡顿总数      ： ' + str(block_cnt))
            logger.info('拉流平均码率      ： ' + str(bps)+ ' kbps')
            logger.info('拉流平均帧率      ： ' + str(fps))
            logger.info('拉流平均画面质量  ： ' + str(vqoe))

            result_dict['holoWan_rx_rate'] = rx_rate
            result_dict['mediatools_pull_bps'] = bps
            result_dict['mediatools_pull_block_cnt'] = block_cnt
            result_dict['mediatools_pull_fps'] = fps
            result_dict['mediatools_pull_vqoe'] = vqoe

            #保存测试结果
            csv_file_name = result_manager.addResult(result_dict, holowan_config)
            logger.info('测试结果存储到文件： ' + csv_file_name)

        except Exception as e:
            logger.info(str(e)) 
            #处理异常后，主动停止任务
            stop_ret = mediatools.stop_monitor_task_test(str(task_id))
            logger.info(stop_ret)             
#end of method    
