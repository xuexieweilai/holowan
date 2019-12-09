# -*- coding:UTF-8 -*-
#!/usr/bin/python
import requests
import xlrd
import xlwt
import xml.etree.ElementTree as ET
import csv
import sys
import os
import datetime
import time
import hashlib
import numpy as np
from progressbar import ProgressBar     #python3使用如下命令安装progressbar2      sudo python3.7 -m pip install progressbar2
import logging

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

################################################网损配置#################################################################
class holowan(object): 
    # 名   称： __init__
    # 用   途： 初始化holoWAN
    # 作   者： 杨玉松
    # 修改时间： 2019-09-12 
    def __init__(self, host, port):
        self.host = host
        self.port = port
    #end of method

    # 名   称： mergeDefaultParameter
    # 用   途： 将输入参数与默认参数merge
    # 作   者： 杨玉松
    # 修改时间： 2019-09-12 
    def mergeDefaultParameter(self, inputDict={}, defaultDict={}):
        # 将输入参数对应value替换默认参数对应的值
        for key, value in inputDict.items(): 
            defaultDict[key] = value
        return defaultDict
    #end of method

    # 名   称： getPayload
    # 用   途： 根据数据参数生成修改损伤参数的http post playload数据
    # 作   者： 杨玉松
    # 修改时间： 2019-09-12 
    def getPayload(self, pid, pn, uploadDict, downloadDict):
        # 增加根节点
        root = ET.Element('pc')
        egineId = ET.SubElement(root, 'eid')
        egineId.text = "1"

        # 增加pathId
        pathId = ET.SubElement(root, 'pid')
        pathId.text = pid

        # 增加pathName
        pathName = ET.SubElement(root, 'pn')
        pathName.text = pn

        # 增加path损伤方向，默认双向
        pathDrict = ET.SubElement(root, 'pd')
        pathDrict.text = "3"

        # 增加上行损伤参数
        portLeftTr = ET.SubElement(root, 'pltr')
        #############################上行带宽参数配置###################################################
        bandwith_upload = ET.SubElement(portLeftTr, 'bd')

        if str(uploadDict['bandwith_type_upload']) == '1':
            bandwith_type_upload = ET.SubElement(bandwith_upload, 's')
            bandwith_type_upload.text = str(uploadDict['bandwith_type_upload'])

            bandwith_value_upload = ET.SubElement(bandwith_upload, 'r')
            bandwith_value_upload.text = str(uploadDict['bandwith_value_upload'])

            bandwith_t_upload = ET.SubElement(bandwith_upload, 't')
            bandwith_t_upload.text = str(uploadDict['bandwith_t_upload'])
        elif str(uploadDict['bandwith_type_upload']) == '2':  #波动带宽
            bandwith_type_upload = ET.SubElement(bandwith_upload, 's')
            bandwith_type_upload.text = str(uploadDict['bandwith_type_upload'])

            bandwith_t_upload = ET.SubElement(bandwith_upload, 't')
            bandwith_t_upload.text = str(uploadDict['bandwith_t_upload'])

            #波动曲线id
            bandwith_shake_upload = ET.SubElement(bandwith_upload, 'shake', attrib={'type_id': str(uploadDict['bandwith_type_id_upload'])})
            
            #配置最大带宽
            bandwith_max_upload = ET.SubElement(bandwith_shake_upload, 'max')
            bandwith_max_upload.text = str(uploadDict['bandwith_max_upload'])

            #配置最小带宽
            bandwith_min_upload = ET.SubElement(bandwith_shake_upload, 'min')
            bandwith_min_upload.text = str(uploadDict['bandwith_min_upload'])

            #配置曲线参数
            if str(uploadDict['bandwith_type_id_upload']) == '1': #正玄波曲线参数
                bandwith_cycle_upload = ET.SubElement(bandwith_shake_upload, 'cycle')
                bandwith_cycle_upload.text = str(uploadDict['bandwith_cycle_upload'])

                bandwith_phase_upload = ET.SubElement(bandwith_shake_upload, 'phase')
                bandwith_phase_upload.text = str(uploadDict['bandwith_phase_upload'])
            else:#其它曲线参数待实现
                raise('参数错误，待实现')    
        else:
            raise('参数错误')       
        ##############################上行背景流参数配置################################################
        background_upload = ET.SubElement(portLeftTr, 'bg')

        background_status_upload = ET.SubElement(background_upload, 's')
        background_status_upload.text = str(
            uploadDict['background_status_upload'])

        background_lu_upload = ET.SubElement(background_upload, 'lu')
        background_lu_upload.text = str(uploadDict['background_lu_upload'])

        background_bs_upload = ET.SubElement(background_upload, 'bs')
        background_bs_upload.text = str(uploadDict['background_bs_upload'])
        ##############################上行队列深度参数配置################################################
        queuelength_upload = ET.SubElement(portLeftTr, 'ql')

        queue_deth_upload = ET.SubElement(queuelength_upload, 'qd')
        queue_deth_upload.text = str(uploadDict['queue_deth_upload'])

        queue_qdt_upload = ET.SubElement(queuelength_upload, 'qdt')
        queue_qdt_upload.text = str(uploadDict['queue_qdt_upload'])
        ##############################上行修改报文参数配置################################################
        modify_upload = ET.SubElement(portLeftTr, 'md')

        modify_cs_upload = ET.SubElement(modify_upload, 'cs')
        modify_cs_upload.text = str(uploadDict['modify_cs_upload'])
        ##############################上行MTU参数配置################################################
        mtu_upload = ET.SubElement(portLeftTr, 'm')

        mtu_s_upload = ET.SubElement(mtu_upload, 's')
        mtu_s_upload.text = str(uploadDict['mtu_s_upload'])

        mtu_n_upload = ET.SubElement(mtu_upload, 'n')
        mtu_n_upload.text = str(uploadDict['mtu_n_upload'])
        ##############################上行for参数配置################################################
        frameoverheadr_upload = ET.SubElement(portLeftTr, 'fo')

        frameoverheadr_t_upload = ET.SubElement(frameoverheadr_upload, 't')
        frameoverheadr_t_upload.text = str(
            uploadDict['frameoverheadr_t_upload'])

        frameoverheadr_r_upload = ET.SubElement(frameoverheadr_upload, 'r')
        frameoverheadr_r_upload.text = str(
            uploadDict['frameoverheadr_r_upload'])
        ##############################上行delay参数配置################################################
        delay_upload = ET.SubElement(portLeftTr, 'd')

        delay_type_upload = ET.SubElement(delay_upload, 's')
        delay_type_upload.text = str(uploadDict['delay_type_upload'])

        if str(uploadDict['delay_type_upload']) == '1':
            # 常量时延
            delay_co_upload = ET.SubElement(delay_upload, 'co')
            delay_de_upload = ET.SubElement(delay_co_upload, 'de')
            delay_de_upload.text = str(uploadDict['delay_const_upload'])
        elif str(uploadDict['delay_type_upload']) == '2':
            # 平均分布时延
            delay_un_upload = ET.SubElement(delay_upload, 'un')
            # 最小值
            delay_dmi_upload = ET.SubElement(delay_un_upload, 'dmi')
            delay_dmi_upload.text = str(uploadDict['delay_dmi_upload'])
            # 最大值
            delay_dma_upload = ET.SubElement(delay_un_upload, 'dma')
            delay_dma_upload.text = str(uploadDict['delay_dma_upload'])
            # 是否乱序
            delay_reo_upload = ET.SubElement(delay_un_upload, 'reo')
            delay_reo_upload.text = str(uploadDict['delay_reo_upload'])
            # 波动曲线
            delay_shake_upload = ET.SubElement(
                delay_un_upload, 'shake', attrib={'type_id': "0"})
        elif str(uploadDict['delay_type_upload']) == '3':
            # 正太分布时延
            delay_no_upload = ET.SubElement(delay_upload, 'no')
            # 最小值
            delay_de_upload = ET.SubElement(delay_no_upload, 'de')
            delay_de_upload.text = str(uploadDict['delay_de_upload'])
            # 最大值
            delay_me_upload = ET.SubElement(delay_no_upload, 'me')
            delay_me_upload.text = str(uploadDict['delay_me_upload'])
            # 标准差
            delay_sd_upload = ET.SubElement(delay_no_upload, 'sd')
            delay_sd_upload.text = str(uploadDict['delay_sd_upload'])   
            #是否乱序
            delay_reo_upload = ET.SubElement(delay_no_upload, 'reo')
            delay_reo_upload.text = str(uploadDict['delay_reo_upload'])                        
        else:
            raise('参数错误')
        ##############################上行丢包参数配置################################################
        loss_upload = ET.SubElement(portLeftTr, 'l')

        loss_type_upload = ET.SubElement(loss_upload, 's')
        loss_type_upload.text = str(uploadDict['loss_type_upload'])

        if str(uploadDict['loss_type_upload']) == '1':
            loss_ra_upload = ET.SubElement(loss_upload, 'ra')
            # 最小值
            loss_r_upload = ET.SubElement(loss_ra_upload, 'r')
            loss_r_upload.text = str(uploadDict['loss_r_upload'])

        # elif str(uploadDict['loss_type_upload']) == '2':
            # todo
        # elif str(uploadDict['loss_type_upload']) == '3':
            # todo
        else:
            raise('丢包参数错误')
        ##############################上行bit error参数配置#############################################
        biterror_upload = ET.SubElement(portLeftTr, 'cor')

        biterror_ber_upload = ET.SubElement(biterror_upload, 'ber')
        biterror_ber_upload.text = str(uploadDict['biterror_ber_upload'])

        biterror_beri_upload = ET.SubElement(biterror_upload, 'beri')
        biterror_beri_upload.text = str(uploadDict['biterror_beri_upload'])

        ##############################上行乱序参数配置##################################################
        reordering_upload = ET.SubElement(portLeftTr, 'reo')

        reordering_s_upload = ET.SubElement(reordering_upload, 's')
        reordering_s_upload.text = str(uploadDict['reordering_s_upload'])

        reordering_p_upload = ET.SubElement(reordering_upload, 'p')
        reordering_p_upload.text = str(uploadDict['reordering_p_upload'])

        reordering_dmi_upload = ET.SubElement(reordering_upload, 'dmi')
        reordering_dmi_upload.text = str(uploadDict['reordering_dmi_upload'])

        reordering_dma_upload = ET.SubElement(reordering_upload, 'dma')
        reordering_dma_upload.text = str(uploadDict['reordering_dma_upload'])

        ##############################上行重复帧参数配置################################################
        duplication_upload = ET.SubElement(portLeftTr, 'du')

        reordering_s_upload = ET.SubElement(duplication_upload, 's')
        reordering_s_upload.text = str(uploadDict['reordering_s_upload'])

        duplication_p_upload = ET.SubElement(duplication_upload, 'p')
        duplication_p_upload.text = str(uploadDict['duplication_p_upload'])
        #############################################################################################

        # 增加下行损伤参数
        portRightTr = ET.SubElement(root, 'prtl')
        #############################下行带宽参数配置###################################################
        bandwith_download = ET.SubElement(portRightTr, 'bd')

        if str(downloadDict['bandwith_type_download']) == '1':#FIX带宽
            bandwith_type_download = ET.SubElement(bandwith_download, 's')
            bandwith_type_download.text = str(downloadDict['bandwith_type_download'])

            bandwith_value_download = ET.SubElement(bandwith_download, 'r')
            bandwith_value_download.text = str(downloadDict['bandwith_value_download'])

            bandwith_t_download = ET.SubElement(bandwith_download, 't')
            bandwith_t_download.text = str(downloadDict['bandwith_t_download'])
        elif str(downloadDict['bandwith_type_download']) == '2':#波动带宽
            bandwith_type_download = ET.SubElement(bandwith_download, 's')
            bandwith_type_download.text = str(downloadDict['bandwith_type_download'])

            bandwith_t_download = ET.SubElement(bandwith_download, 't')
            bandwith_t_download.text = str(downloadDict['bandwith_t_download'])

            #配置曲线id
            bandwith_shake_download = ET.SubElement(bandwith_download, 'shake', attrib={'type_id': str(downloadDict['bandwith_type_id_download'])})

            #配置曲线最大带宽
            bandwith_max_download = ET.SubElement(bandwith_shake_download, 'max')
            bandwith_max_download.text = str(downloadDict['bandwith_max_download'])

            #配置曲线最小带宽
            bandwith_min_download = ET.SubElement(bandwith_shake_download, 'min')
            bandwith_min_download.text = str(downloadDict['bandwith_min_download'])

            #配置曲线参数
            if str(downloadDict['bandwith_type_id_download']) == '1': #正玄波参数配置
                bandwith_cycle_download = ET.SubElement(bandwith_shake_download, 'cycle')
                bandwith_cycle_download.text = str(downloadDict['bandwith_cycle_download'])

                bandwith_phase_download = ET.SubElement(bandwith_shake_download, 'phase')
                bandwith_phase_download.text = str(downloadDict['bandwith_phase_download'])
            else:#其它曲线参数待实现
                raise('参数错误，待实现')    
        else:
            raise('参数错误')  
        ##############################下行背景流参数配置################################################
        background_download = ET.SubElement(portRightTr, 'bg')

        background_status_download = ET.SubElement(background_download, 's')
        background_status_download.text = str(
            downloadDict['background_status_download'])

        background_lu_download = ET.SubElement(background_download, 'lu')
        background_lu_download.text = str(
            downloadDict['background_lu_download'])

        background_bs_download = ET.SubElement(background_download, 'bs')
        background_bs_download.text = str(
            downloadDict['background_bs_download'])
        ##############################下行队列深度参数配置################################################
        queuelength_download = ET.SubElement(portRightTr, 'ql')

        queue_deth_download = ET.SubElement(queuelength_download, 'qd')
        queue_deth_download.text = str(downloadDict['queue_deth_download'])

        queue_qdt_download = ET.SubElement(queuelength_download, 'qdt')
        queue_qdt_download.text = str(downloadDict['queue_qdt_download'])
        ##############################下行修改报文参数配置################################################
        modify_download = ET.SubElement(portRightTr, 'md')

        modify_cs_download = ET.SubElement(modify_download, 'cs')
        modify_cs_download.text = str(downloadDict['modify_cs_download'])
        ##############################下行MTU参数配置################################################
        mtu_download = ET.SubElement(portRightTr, 'm')

        mtu_s_download = ET.SubElement(mtu_download, 's')
        mtu_s_download.text = str(downloadDict['mtu_s_download'])

        mtu_n_download = ET.SubElement(mtu_download, 'n')
        mtu_n_download.text = str(downloadDict['mtu_n_download'])
        ##############################下行for参数配置################################################
        frameoverheadr_download = ET.SubElement(portRightTr, 'fo')

        frameoverheadr_t_download = ET.SubElement(frameoverheadr_download, 't')
        frameoverheadr_t_download.text = str(
            downloadDict['frameoverheadr_t_download'])

        frameoverheadr_r_download = ET.SubElement(frameoverheadr_download, 'r')
        frameoverheadr_r_download.text = str(
            downloadDict['frameoverheadr_r_download'])
        ##############################下行delay参数配置################################################
        delay_download = ET.SubElement(portRightTr, 'd')

        delay_type_download = ET.SubElement(delay_download, 's')
        delay_type_download.text = str(downloadDict['delay_type_download'])

        if str(downloadDict['delay_type_download']) == '1':
            # 常量时延
            delay_co_download = ET.SubElement(delay_download, 'co')
            delay_de_download = ET.SubElement(delay_co_download, 'de')
            delay_de_download.text = str(downloadDict['delay_const_download'])
        elif str(downloadDict['delay_type_download']) == '2':
            # 平均分布时延
            delay_un_download = ET.SubElement(delay_download, 'un')
            # 最小值
            delay_dmi_download = ET.SubElement(delay_un_download, 'dmi')
            delay_dmi_download.text = str(downloadDict['delay_dmi_download'])
            # 最大值
            delay_dma_download = ET.SubElement(delay_un_download, 'dma')
            delay_dma_download.text = str(downloadDict['delay_dma_download'])
            # 是否乱序
            delay_reo_download = ET.SubElement(delay_un_download, 'reo')
            delay_reo_download.text = str(downloadDict['delay_reo_download'])
            # 波动曲线
            delay_shake_download = ET.SubElement(
                delay_un_download, 'shake', attrib={'type_id': "0"})
        elif str(downloadDict['delay_type_download']) == '3':
            # 正太分布时延
            delay_no_download = ET.SubElement(delay_download, 'no')
            # 最小值
            delay_de_download = ET.SubElement(delay_no_download, 'de')
            delay_de_download.text = str(downloadDict['delay_de_download'])
            # 最大值
            delay_me_download = ET.SubElement(delay_no_download, 'me')
            delay_me_download.text = str(downloadDict['delay_me_download'])
            # 标准差
            delay_sd_download = ET.SubElement(delay_no_download, 'sd')
            delay_sd_download.text = str(downloadDict['delay_sd_download'])   
            #是否乱序
            delay_reo_download = ET.SubElement(delay_no_download, 'reo')
            delay_reo_download.text = str(downloadDict['delay_reo_download'])    
        else:
            raise('参数错误')
        ##############################下行丢包参数配置################################################
        loss_download = ET.SubElement(portRightTr, 'l')

        loss_type_download = ET.SubElement(loss_download, 's')
        loss_type_download.text = str(downloadDict['loss_type_download'])

        if str(downloadDict['loss_type_download']) == '1':
            loss_ra_download = ET.SubElement(loss_download, 'ra')
            # 最小值
            loss_r_download = ET.SubElement(loss_ra_download, 'r')
            loss_r_download.text = str(downloadDict['loss_r_download'])

        # elif str(downloadDict['loss_type_download']) == '2':
            # todo
        # elif str(downloadDict['loss_type_download']) == '3':
            # todo
        else:
            raise('丢包参数错误')
        ##############################下行bit error参数配置#############################################
        biterror_download = ET.SubElement(portRightTr, 'cor')

        biterror_ber_download = ET.SubElement(biterror_download, 'ber')
        biterror_ber_download.text = str(downloadDict['biterror_ber_download'])

        biterror_beri_download = ET.SubElement(biterror_download, 'beri')
        biterror_beri_download.text = str(
            downloadDict['biterror_beri_download'])

        ##############################下行乱序参数配置##################################################
        reordering_download = ET.SubElement(portRightTr, 'reo')

        reordering_s_download = ET.SubElement(reordering_download, 's')
        reordering_s_download.text = str(downloadDict['reordering_s_download'])

        reordering_p_download = ET.SubElement(reordering_download, 'p')
        reordering_p_download.text = str(downloadDict['reordering_p_download'])

        reordering_dmi_download = ET.SubElement(reordering_download, 'dmi')
        reordering_dmi_download.text = str(
            downloadDict['reordering_dmi_download'])

        reordering_dma_download = ET.SubElement(reordering_download, 'dma')
        reordering_dma_download.text = str(
            downloadDict['reordering_dma_download'])

        ##############################下行重复帧参数配置################################################
        duplication_download = ET.SubElement(portRightTr, 'du')

        reordering_s_download = ET.SubElement(duplication_download, 's')
        reordering_s_download.text = str(downloadDict['reordering_s_download'])

        duplication_p_download = ET.SubElement(duplication_download, 'p')
        duplication_p_download.text = str(
            downloadDict['duplication_p_download'])
        #############################################################################################

        #et = ET.ElementTree(root)
        #et.write('1.xml', encoding="utf-8", xml_declaration=True)
        elem_data = ET.tostring(root, encoding='utf8', method='xml')
        return elem_data
    #end of method

    # 名   称： get_statistics_information
    # 用   途： 获取当前设备的概要信息，用于保存配置
    # 作   者： 杨玉松
    # 修改时间： 2019-09-12
    def get_statistics_information(self):
        url = "http://" + self.host + ":" + self.port + "/statistics_information"
        logger.debug('url : ' + url)

        headers = {"X-holowan-API": "OI_API"}

        response = requests.get(url, headers=headers)
        logger.debug('response.status_code : ' + str(response.status_code))

        if response.status_code == 200:
            logger.debug(response.text)           
            return response.text
        else:
            logger.error('response.status_code : ' + str(response.status_code))
            raise Exception('response.status_code : ' + str(response.status_code))
    #end of method

    # 名   称： get_statistics_information_with_pid
    # 用   途： 获取当前path的概要信息
    # 作   者： 杨玉松
    # 修改时间： 2019-10-15
    def get_statistics_information_with_pid(self, pid):
        holowan_config = {}
        url = "http://" + self.host + ":" + self.port + "/statistics_information"
        logger.debug('url : ' + url)

        headers = {"X-holowan-API": "OI_API"}

        response = requests.get(url, headers=headers)
        logger.debug('response.status_code : ' + str(response.status_code))

        if response.status_code == 200:
            logger.debug(response.text)           
            root = ET.fromstring(response.text)
            for node in root.findall("e/ep/p"): 
                if str(node.findtext("pi"))  == str(pid):
                    holowan_config['upload'] = node.findtext("l")
                    holowan_config['download'] = node.findtext("r")
            return  holowan_config           
        else:
            logger.error('response.status_code : ' + str(response.status_code))
            raise Exception('response.status_code : ' + str(response.status_code))
    #end of method

    # 名   称： save_engine_emulator_config
    # 用   途： 保存当前配置
    # 作   者： 杨玉松
    # 修改时间： 2019-09-12
    def save_engine_emulator_config(self):
        url = "http://" + self.host + ":" + self.port + "/emulator_config"
        logger.debug('url : ' + url)
    
        payload = self.get_statistics_information()
        logger.debug('payload: ' + str(payload))

        urlMd5 = hashlib.md5("/emulator_config".encode(encoding='UTF-8')).hexdigest()
        bodyMd5 = hashlib.md5(payload.encode(encoding='UTF-8')).hexdigest()

        headers = {"X-holowan-API": "OI_API" , "URL-MD5": urlMd5, "Body-MD5": bodyMd5}

        response = requests.post(url, data=payload, headers=headers)
        dict1 = response.json()
        logger.info(dict1) 
               
        if str(dict1['errCode']) != "0":
            logger.error(str(dict1['errMsg']))
            raise Exception(dict1['errMsg'])
    #end of method   

    # 名   称： get_current_resault_data
    # 用   途： 获取当前实时数据
    # 作   者： 杨玉松
    # 修改时间： 2019-09-26
    def get_current_resault_data(self):
        url = "http://" + self.host + ":" + self.port + "/current_resault_data?engine=1&path=1-2-3-4-5-6-7-8-9"
        logger.debug('url : ' + url)

        headers = {"X-holowan-API": "OI_API" }

        response = requests.get(url, headers=headers)
        return response.content
    #end of method 

    # 名   称： get_rx_rate_avg
    # 用   途： 获取码率平均值
    # 参   数： pid     --必选参数，pathid
    #          direct  --必选参数，可选值upload、download，想要获取码率均值的方向
    #          times   --可选参数，获取码率采样点个数，默认600秒
    # 作   者： 杨玉松
    # 修改时间： 2019-09-26   
    def get_rx_rate_avg(self, pid, direct,times = 600):
        list1 = []
        pbar = ProgressBar()    #打印进度条
        for i in pbar(range(1,times)): 
            try:
                sourceDate  = self.get_current_resault_data()
                root = ET.fromstring(sourceDate)
                for node in root.findall("path"):  
                    if str(node.findtext("path_id"))  == str(pid):
                        if str(direct) == 'upload':
                            text = node.findtext("left_to_right/rx_rate")
                        elif str(direct) == 'download': 
                            text = node.findtext("right_to_left/rx_rate")
                        else:
                            raise('参数direct错误，请重新输入')
                list1.append(int(text))
                time.sleep(1)
                #打印进度条
                #print("progress:{0}%".format(round((i + 1) * 100 / times)), end="\r")
            except Exception as e:
                logger.info('Error:  ' + str(e)) 
                continue    
        #记录过程数据并返回平均值，单位kbps
        logger.debug(list1)    
        avg = np.mean(list1, dtype = int)
        return avg//1000
    #end of method
         
    # 名   称： path_emulator_config
    # 用   途： 修改网损参数
    # 参   数： pid --必选参数，PATH id
    #          pn --必选参数，PATH name 
    #          uploadDict --必选参数，上行网损参数dict
    #               bandwith_type_upload    --可选参数，带宽类型，1为FIX，2为波动，默认为1
    #               bandwith_value_upload   --可选参数，FIX类型带宽值
    #               loss_type_upload        --可选参数，丢包类型，1为随机丢包，默认为1
    #               loss_r_upload           --随机丢包比例
    #               delay_type_upload       --可选参数，延时类型，1为固定延时constant，2位平均分布延时，3为正态分布延时
    #               delay_const_upload      --可选参数，常量延时值
    #               delay_dmi_upload        --可选参数，平均分布延时最小值
    #               delay_dma_upload        --可选参数，平均分布延时最大值
    #          downloadDict --必选参数，下行网损参数dict
    #               bandwith_type_download    --可选参数，带宽类型，1为FIX，2为波动，默认为1
    #               bandwith_value_download   --可选参数，FIX类型带宽值
    #               loss_type_download        --可选参数，丢包类型，1为随机丢包，默认为1
    #               loss_r_download           --随机丢包比例
    #               delay_type_download       --可选参数，延时类型，1为固定延时constant，2位平均分布延时，3为正态分布延时
    #               delay_const_download      --可选参数，常量延时值
    #               delay_dmi_download        --可选参数，平均分布延时最小值
    #               delay_dma_download        --可选参数，平均分布延时最大值 

    # 使用举例：     
    #   uploadDict = {'bandwith_value_upload': "111", 'loss_r_upload':10}
    #   downloadDict = {'bandwith_value_download': "222"}
    #   holowan = holowan('192.168.1.199', "8080")
    #   holowan.path_emulator_config("9", "PATH 9",  uploadDict, downloadDict)
    #
    # 作   者： 杨玉松
    # 修改时间： 2019-08-31
    def path_emulator_config(self, pid, pn, uploadDict={}, downloadDict={}):
        self.pid = pid
        self.pn = pn

        # 所有损伤参数默认值，待添加默认值
        defaultUploadDict = {'bandwith_type_upload': 1, 'bandwith_value_upload': 1000, 'bandwith_t_upload': 3,
                             'bandwith_type_id_upload': 1, 'bandwith_max_upload': 100, 'bandwith_min_upload': 10, 'bandwith_cycle_upload': 60, 'bandwith_phase_upload': 0,
                             'background_status_upload': 1, 'background_lu_upload': 0, 'background_bs_upload': 0,
                             'queue_deth_upload': 16, 'queue_qdt_upload': 2, 'modify_cs_upload': 0, 'mtu_s_upload': 1,
                             'mtu_n_upload': 1500, 'frameoverheadr_t_upload': 1, 'frameoverheadr_r_upload': 24,
                             'delay_type_upload': 1, 'delay_const_upload': 0, 'delay_dmi_upload': 0, 'delay_dma_upload': 50,
                             'delay_de_upload': 1, 'delay_me_upload': 50, 'delay_sd_upload': 10, 'delay_reo_upload': 0, 
                             'loss_type_upload': 1, 'loss_r_upload': 0, 'biterror_ber_upload': 0, 'biterror_beri_upload': 14, 
                             'reordering_s_upload': 1, 'reordering_p_upload': 0, 'reordering_dmi_upload': '0.1',
                             'reordering_dma_upload': '0.5', 'reordering_s_upload': 1, 'duplication_p_upload': 0}

        defaultDownloadDict = {'bandwith_type_download': 1, 'bandwith_value_download': 1000, 'bandwith_t_download': 3,
                               'bandwith_type_id_download': 1, 'bandwith_max_download': 100, 'bandwith_min_download': 10, 'bandwith_cycle_download': 60, 'bandwith_phase_download': 0,
                               'background_status_download': 1, 'background_lu_download': 0, 'background_bs_download': 0,
                               'queue_deth_download': 16, 'queue_qdt_download': 2, 'modify_cs_download': 0, 'mtu_s_download': 1,
                               'mtu_n_download': 1500, 'frameoverheadr_t_download': 1, 'frameoverheadr_r_download': 24,
                               'delay_type_download': 1, 'delay_const_download': 0, 'delay_dmi_download': 0, 'delay_dma_download': 50,
                               'delay_de_download': 1, 'delay_me_download': 50, 'delay_sd_download': 10, 'delay_reo_download': 0, 
                               'loss_type_download': 1, 'loss_r_download': 0, 'biterror_ber_download': 0, 'biterror_beri_download': 14, 
                               'reordering_s_download': 1, 'reordering_p_download': 0, 'reordering_dmi_download': '0.1',
                               'reordering_dma_download': '0.5', 'reordering_s_download': 1, 'duplication_p_download': 0}

        # 将用户输入的损伤参数值，替换掉对应的默认损伤参数
        defaultUploadDict = self.mergeDefaultParameter(
            uploadDict, defaultUploadDict)
        defaultDownloadDict = self.mergeDefaultParameter(
            downloadDict, defaultDownloadDict)

        # 构造http request payload内容，xml格式并转换成string
        payload = self.getPayload(self.pid, self.pn, defaultUploadDict, defaultDownloadDict)
        logger.debug('payload: ' + str(payload))

        url = "http://" + self.host + ":" + self.port + "/emulator_config"
        logger.debug('url : ' + url)

        urlMd5 = hashlib.md5("/emulator_config".encode(encoding='UTF-8')).hexdigest()
        bodyMd5 = hashlib.md5(payload).hexdigest()

        headers = {"X-holowan-API": "OI_API" , "URL-MD5": urlMd5, "Body-MD5": bodyMd5}

        response = requests.post(url, data=payload, headers=headers)
        dict1 = response.json()
        logger.info(dict1)

        if str(dict1['errCode']) != "0":
            logger.error(str(dict1['errMsg']))
            raise Exception(dict1['errMsg'])
    #end of method

#end of class       