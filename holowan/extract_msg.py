import json
import os


def extract_msg():
    # TODO Delay-Normal的过滤
    file_dir_path = '/Users/lixingda/Downloads/random_net_config_out'
    write_file_path = '/Users/lixingda/Downloads/new_config.txt'
    n = 0
    holowan_list = []
    for file in os.listdir(file_dir_path):
        n += 1
        jitter_dict = {'id': n,
                       'uploadDict': {},
                       'downloadDict': {}
                       }

        with open(file_dir_path + '/' + file , 'r') as new_file:
            content = new_file.read()
            new_content = json.loads(content)
            for key, value in new_content.items():
                if key == 'bandwidth':
                    if value['type'] == 'jitter':
                        # bandwith_type_upload 限制带宽类型[1. 正常模式， 2. 抖动模式]
                        jitter_dict['uploadDict']['bandwith_type_upload'] = 2
                        for key_kids in value.keys():
                            if key_kids == 'jitter_min_kbps':
                                jitter_dict['uploadDict']['bandwith_min_upload'] = value['jitter_min_kbps']

                            if key_kids == 'jitter_max_kbps':
                                jitter_dict['uploadDict']['bandwith_max_upload'] = value['jitter_max_kbps']

                            if key_kids == 'jitter_period_s':
                                jitter_dict['uploadDict']['bandwith_cycle_upload'] = value['jitter_period_s']

                            if key_kids == 'jitter_wave':
                                if value['jitter_wave'] == 'sine':
                                    jitter_dict['uploadDict']['bandwith_type_id_upload'] = '1'
                                if value['jitter_wave'] == 'sawtooth':
                                    jitter_dict['uploadDict']['bandwith_type_id_upload'] = '5'

                                if value['jitter_wave'] == 'polyline_wave':
                                    jitter_dict['uploadDict']['bandwith_type_id_upload'] = '2'
                    if value['type'] == 'fixed':
                        jitter_dict['uploadDict']['bandwith_type_upload'] = 1
                        for key_kids in value.keys():
                            if key_kids == 'fixed_value_kbps':
                                jitter_dict['uploadDict']['bandwith_value_upload'] = value['fixed_value_kbps']

                if key == 'propagation':
                    if value['type'] == 'uniform':
                        jitter_dict['uploadDict']['delay_type_upload'] = '2'
                        for key_kids in value.keys():
                            if key_kids == 'uniform_min_ms':
                                jitter_dict['uploadDict']['delay_dmi_upload'] = value['uniform_min_ms']
                            if key_kids == 'uniform_max_ms':
                                jitter_dict['uploadDict']['delay_dma_upload'] = value['uniform_max_ms']
                            if key_kids == 'uniform_reorder':
                                if value['uniform_reorder'] == True:
                                    jitter_dict['uploadDict']['delay_reo_upload'] = 1
                                if value['uniform_reorder'] == False:
                                    jitter_dict['uploadDict']['delay_reo_upload'] = 0
                    if value['type'] == 'fixed':
                        jitter_dict['uploadDict']['delay_type_upload'] = '1'
                        jitter_dict['uploadDict']['bandwith_value_upload'] = value['fixed_value_ms']

                if key == 'loss':
                    '''丢包类型： 1： Random'''
                    if value['type'] == 'percent':
                        jitter_dict['uploadDict']['loss_type_upload'] = '1'
                        jitter_dict['uploadDict']['loss_r_upload'] = value['percent']

                if key == 'queue_depth':
                    if value['type'] == 'packets':
                        jitter_dict['uploadDict']['queue_qdt_upload'] = 1
                        jitter_dict['uploadDict']['queue_deth_upload'] = value['packets']

            holowan_list.append(str(jitter_dict) + ',\n')
    with open(write_file_path, 'w+') as new_con_total:
        new_con_total.write('[')
        new_con_total.writelines(holowan_list)
        new_con_total.write(']')


if __name__ == '__main__':
    extract_msg()